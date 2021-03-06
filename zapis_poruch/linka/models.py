import datetime

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DruhChyby(models.Model):
    class Meta:
        verbose_name_plural = "Druhy Chýb"
        ordering = ('nazov',)

    nazov = models.CharField(max_length=256)

    def __str__(self):
        return self.nazov


class MiestoNaLinke(models.Model):
    class Meta:
        verbose_name_plural = "Miesta Na Linke"
        ordering = ('miesto',)

    miesto = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.miesto



class SposobenaKym(models.Model):
    class Meta:
        verbose_name_plural = "Spôsobené Kým"
        ordering = ('kym',)

    kym = models.CharField(max_length=256)

    def __str__(self):
        return self.kym



class TypChyby(models.Model):
    class Meta:
        verbose_name_plural = "Typy Chýb"

    popis = models.CharField(verbose_name="Popis typu chyby", max_length=256)
    miesto_na_linke = models.ForeignKey(MiestoNaLinke, verbose_name="Pozícia", on_delete=models.CASCADE,  default=None)
    druh_chyby = models.ForeignKey(DruhChyby, verbose_name="Druh chyby", on_delete=models.CASCADE, default=None)
    sposobena_kym = models.ForeignKey(SposobenaKym, verbose_name="Chybu spôsobuje", on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.popis


class TypChybyWrapper:
    def __init__(self, object):
        self.id = object.id
        self._object = object
        self.popis = object.popis
        self.miesto_na_linke = object.miesto_na_linke
        self.druh_chyby = object.druh_chyby
        self.sposobena_kym = object.sposobena_kym
        self.frekvencie = dict()  # todo frekvencia ma znazornovat ze aka doba je medzi pripadmi, vyssie cislo je horsie
        self.vyskyt = dict()
        self.trvanie = 0  # todo teraz sa vypisuje trvanie v dnoch? treba to prerobit na zmysluplne cisla

    def json(self):
        return {
            "id": str(self.id),
            "popis": str(self.popis),
            "miesto_na_linke": str(self.miesto_na_linke),
            "druh_chyby": str(self.druh_chyby),
            "sposobena_kym": str(self.sposobena_kym),
            "frekvencie": self.frekvencie,
            "vyskyt": self.vyskyt,
            "trvanie": self.trvanie
        }

    def _increase_dict(self, dictionary, rozdiel):
        if rozdiel.days <= 7:
            dictionary["week"] += 1
        if rozdiel.days <= 28:
            dictionary["month"] += 1
        if rozdiel.days <= 182:
            dictionary["6months"] += 1
        if rozdiel.days <= 365:
            dictionary["year"] += 1

    def fill(self, objects):
        count = 0
        pocet_vsetkych = {"week": 0, "month": 0, "6months": 0, "year": 0}
        pocet_nasich = {"week": 0, "month": 0, "6months": 0, "year": 0}

        today = datetime.datetime.now()
        today = today.replace(tzinfo=None)
        for object in objects:
            vznik = object.vznik.replace(tzinfo=None)
            rozdiel = today - vznik
            self._increase_dict(pocet_vsetkych, rozdiel)

            if object.typ_chyby != self._object:
                continue
            count += 1
            self.trvanie += object.trvanie.days
            self._increase_dict(pocet_nasich, rozdiel)

        if count == 0:
            self.trvanie = 0
        else:
            self.trvanie = round(self.trvanie / count)  # todo solve ZeroDivisionError on empty DB
        self.vyskyt = pocet_nasich
        for key in pocet_nasich:
            self.frekvencie[key] = 0 if pocet_vsetkych[key] == 0 else pocet_nasich[key] / pocet_vsetkych[key]

    @staticmethod
    def all():
        objects = TypChyby.objects.all()
        return [TypChybyWrapper(x) for x in objects]


class DruhRevizie(models.Model):
    class Meta:
        verbose_name_plural = "Typy revízie"
        ordering = ('nazov',)

    nazov = models.CharField('Názov typu revízie', max_length=256,  default=None)

    def __str__(self):
        return self.nazov


class TypRevizie(models.Model):
    """toto popisuje celu reviziu"""
    class Meta:
        verbose_name_plural = "Revízie"
        ordering = ('nazov_revizie',)

    nazov_revizie = models.CharField('Názov revízie', max_length=256,  default=None)
    typ_revizie = models.ForeignKey(DruhRevizie, verbose_name="Typ revízie", on_delete=models.CASCADE, default=None)
    datum_poslednej_revizie = models.DateField('Dátum poslednej revízie')
    exspiracia = models.IntegerField('Expirácia', default=365)
    datum_nadchadzajucej_revizie = models.DateField('Dátum nadchádzajúcej revízie')

    def __str__(self):
        return self.nazov_revizie


# zaznam o chybe
class Chyba(models.Model):
    class Meta:
        verbose_name_plural = "Chyby"

    typ_chyby = models.ForeignKey(TypChyby, verbose_name="Typ Chyby", on_delete=models.CASCADE,
                                  default=None, blank=True, null=True)

    #stav
    schvalena = models.BooleanField(verbose_name="Schválená", default=False)
    vyriesena = models.BooleanField(verbose_name="Vyriešená", blank=True, default=False)

    # cas vzniku a vyriesenia
    vznik = models.DateTimeField(verbose_name="Čas vzniku", default=None)
    vyriesenie = models.DateTimeField(verbose_name="Čas vyriešenia", default=None, blank=True, null=True)

    # clovek kto nahlasil chybu
    pouzivatel = models.ForeignKey(User, verbose_name="Používateľ", on_delete=models.CASCADE,
                                   default=None, null=True)

    # pozicia
    miesto_na_linke = models.ForeignKey(MiestoNaLinke, verbose_name="Pozícia",  on_delete=models.CASCADE,
                                        default=None, null=True)
    # mechanicka elektronicka
    druh_chyby = models.ForeignKey(DruhChyby, verbose_name="Druh chyby",  on_delete=models.CASCADE,
                                   default=None, null=True)
    # stroj/clovek
    sposobena_kym = models.ForeignKey(SposobenaKym, verbose_name="Chybu spôsobil",  on_delete=models.CASCADE,
                                      default=None, null=True)

    popis = models.CharField(verbose_name="Popis", max_length=128, default=None, null=True, blank=False)
    dovod = models.CharField(verbose_name="Dôvod", max_length=128, default=None, blank=True, null=True)
    opatrenia = models.CharField(verbose_name="Opatrenia/ Oprava", max_length=256,  default=None, blank=True, null=True)
    nahradny_diel = models.CharField(verbose_name="Náhradný diel", max_length=128,  default=None, blank=True, null=True)

    def __str__(self):
        vyriesena = 'Nevyriešená' if not self.vyriesena else 'Vyriešená' if self.schvalena else 'Vyriešená (čaká na potvrdenie)'
        return f'{self.vznik} | {vyriesena} | {self.popis} | {self.dovod}'


class ChybaWrapper:
    def __init__(self, object):
        self.id = object.id
        self.vznik = object.vznik
        self.pouzivatel = object.pouzivatel
        self.schvalena = object.schvalena
        self.vyriesena = object.vyriesena
        self.vyriesenie = object.vyriesenie
        self.miesto_na_linke = object.miesto_na_linke
        self.druh_chyby = object.druh_chyby
        self.sposobena_kym = object.sposobena_kym
        self.typ_chyby = object.typ_chyby
        self.opatrenia = object.opatrenia
        self.nahradny_diel = object.nahradny_diel
        self.popis = object.popis
        self.dovod = object.dovod
        self.trvanie = datetime.timedelta(days=0) if self.vyriesenie is None else self.vyriesenie - self.vznik

    @staticmethod
    def all():
        objects = Chyba.objects.all()
        return [ChybaWrapper(x) for x in objects]
