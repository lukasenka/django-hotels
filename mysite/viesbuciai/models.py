from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError


class Profile(models.Model):
    """
    Pagrindinis profilis prisiregistravusiam useriui.
    Priskyrimas sukuriamas automatiškai panaudojus signalus.
    Naudojami laukai : vartotojo, vardo, pavardės ir kitos informacijos gavimui.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField("Vardas", max_length=15, null=True, blank=True)
    lastname = models.CharField("Pavarde", max_length=15, null=True, blank=True)
    birth_date = models.DateField("Gimimo Data", null=True, blank=True)
    address = models.CharField("Adresas", max_length=50, null=True, blank=True)
    city = models.CharField("Miestas", max_length=20, null=True, blank=True)
    country = models.CharField("Salis", max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.lastname}"


class Balance(models.Model):

    """
    Balanco likutis yra pririštas per ryšį su userio autorizacija iš django lentelės.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    balance = models.FloatField("Balance", max_length=10, default=0)

    def __str__(self):
        return f"{self.user} {self.balance}"


class Hotel(models.Model):

    """
    Pagrindinis modelis viešbučių lentelėms.
    Pavadinimas, tipas, kaina ir kitos eilutės.
    Prie žmonių kieko pridėta apribojimas dėl esamo filtro (ieškoti pagal max žmonių kiekį)
    Max žmonių kiekis - 4.
    Sutvarkyta kainos ir žmonių kieko validacija (negali būti neigiamas)
    """

    TYPES = (
        ('v', 'VIP'),
        ('g', 'GOLD'),
        ('p', 'PREMIUM'),
        ('s', 'STANDART')
    )

    name = models.CharField("Viesbucio_pavadinimas", max_length=30, null=True)

    type = models.CharField(
        max_length=1,
        choices=TYPES,
        blank=True,
        default='s',
        help_text='Viesbucio tipas'
    )

    STARS = (
        ('1', '*'),
        ('2', '**'),
        ('3', '***'),
        ('4', '****'),
        ('5', '*****')
    )

    stars = models.CharField(
        max_length=1,
        choices=STARS,
        blank=True,
        default='s',
        help_text='Zvaigzduciu kiekis'
    )

    description = models.TextField('Aprasymas', max_length=2000, default='Super hotel')
    address = models.TextField("Viesbucio_adresas", default="Adresas", max_length=200)
    price = models.FloatField("Viesbucio_kaina", null=True)
    quantity = models.IntegerField("Zmoniu_kiekis", default=1, validators=[MaxValueValidator(4)])
    availability = models.IntegerField("Kiekis")

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name}"

    # Kainos ir žmonių kieko neigiamo skaičiaus sutvarkymas
    def clean(self):
        if self.price < 0:
            raise ValidationError({'price': ['Kaina negali būti neigiama.']})
        elif self.availability < 0:
            raise ValidationError({'availability': ['Žmonių kiekis negali būti neigiamas.']})
        super().clean()


class Order(models.Model):
    """
    Pagrindinė užsakymo lentelė.
    Klientas gaunamas per ryšį (ForeignKey) iš Profilio modelio.
    Nustatomi datos, uzsakymo ir kiti laukai.
    Hotelis gaunamas per ryšį (ForeignKey) iš Hotel modelio.
    Admin detalės gaunamos per ryšį iš AdminDetails ir iškart sukuriamas
    atlikus užsakymą.
    """
    client = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True)
    order_date = models.DateField("Uzsakymo_data", auto_now_add=True, null=True, blank=True)
    r_date = models.DateField("Registracijos_data", null=True, blank=True)
    i_date = models.DateField("Isvykimo_data", null=True, blank=True)
    hotel = models.ForeignKey("Hotel", on_delete=models.SET_NULL, null=True)

    STATUS = (
        ('u', 'Uzsakyta'),
        ('r', 'Ruosiama'),
        ('p', 'Paruosta'),
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS,
        blank=True,
        default='u',
        help_text='Status'
    )

    admin_details = models.OneToOneField("AdminDetails", on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.admin_details:
            self.admin_details = AdminDetails.objects.create(client=self.client, room_id=0, aukstas=0,
                                                             ramybes_valandos="Laukiama patvirtinimo")
            self.save()

    def __str__(self):
        return f"{self.client.name} {self.hotel.name}"


class AdminDetails(models.Model):
    """
    Admin detalių modelis.
    Klientas gaunamas iš Profilio modelio per ForeignKey.
    Pridėtos kambario ir aukšto validacijos (negali būti neigiamos)
    """
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    room_id = models.IntegerField("Kambario_numeris")
    aukstas = models.IntegerField("Aukstas")
    ramybes_valandos = models.CharField("Ramybes_valandos", max_length=20)

    # Aukšto ir kambario numerio neigiamo skaičiaus sutvarkymas
    def clean(self):
        if self.room_id < 0:
            raise ValidationError({'room_id': ['Kambario numeris negali būti neigiamas.']})
        elif self.aukstas < 0:
            raise ValidationError({'aukstas': ['Aukštas negali būti neigiamas.']})
        super().clean()

    def __str__(self):
        return f"{self.client.name} {self.room_id} {self.aukstas}"
