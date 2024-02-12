from django.core.paginator import Paginator
from .models import Balance, Hotel, Order, AdminDetails
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, RegistrationForm, HotelSelectForm, OrderForm, EditAdminDetailsForm, \
    EditOrderForm, HotelForm
from .models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from datetime import date


@login_required(login_url="/viesbuciai/accounts/login/")
def profile(request):
    """
    Pagrindinis profilio view'sas
    :param request: automatinė užklausa
    :return: išsaugoma forma po profilio užpildymo ir grįžtama į
    užsakymų sąrašą.
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('hotels')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'profiles/profile.html', {'form': form})


def register(request):
    """
    Registracijos view'as
    :param request: automatinė užklausa.
    :return: išsaugoma užpildyta forma ir nukreipiama
    į prisijungimą, arba (neteisingų duomenų įvedimo atveju) atgal.
    """
    if request.user.is_authenticated:
        return redirect('hotels')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
        else:
            messages.error(request, 'There was an error with your submission. Please correct the errors below.')
            return render(request, 'register.html', {'form': form})
    else:
        form = RegistrationForm()
        return render(request, 'register.html', {'form': form})

# Signalai

#############################


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

#################################


def main_page(request):
    """
    Pagrindinio puslapio view'sas.
    :param request: automatinė užklausa.
    :return: grįžtama atgal į profilį, kol profilis nėra pilnai užpildytas.
    """
    if request.user.is_authenticated:
        profile_ = Profile.objects.get(user=request.user)

        # Naujas vartotojas be balanco
        try:
            balance = Balance.objects.get(user=request.user)
        except ObjectDoesNotExist:
            balance = Balance.objects.create(user=request.user, balance=0)
            balance.save()

        ##########################

        if profile_.name and profile_.lastname and profile_.address and \
                profile_.birth_date and profile_.city and profile_.country:

            context = {
                "balance": round(balance.balance, 2)
            }
            return render(request, 'index.html', context=context)
        else:
            return HttpResponseRedirect('accounts/profile/')
    else:
        return HttpResponseRedirect('accounts/login/')


@login_required(login_url="/viesbuciai/accounts/login/")
def hotels(request):
    """
    Viešbučių view'sas.
    :param request: automatinė užklausa.
    :return: rodoma viešbučių ir balanco informacija.
    Neužpildžius profilio, grįžtama atgal.
    """

    profile_ = Profile.objects.get(user=request.user)
    if profile_.name and profile_.lastname and profile_.address and \
            profile_.birth_date and profile_.city and profile_.country:

        hotels_ = Hotel.objects.all()
        form = HotelSelectForm()

        paginator = Paginator(Hotel.objects.all(), 2)
        page_number = request.GET.get('page')
        paged_hotels = paginator.get_page(page_number)

        context = {
            "hotels": hotels_,
            "form": form,
            "hotels_": paged_hotels
        }

        # Naujas vartotojas neturi balanso - taisom crash.
        try:
            balance = Balance.objects.get(user=request.user)
            rounded = round(balance.balance, 2)
            context['balance'] = rounded
        except ObjectDoesNotExist:
            balance = Balance.objects.create(user=request.user, balance=0)
            balance.save()
            context['balance'] = balance.balance
        #########################################

        return render(request, 'hotels.html', context=context)

    else:

        return HttpResponseRedirect('/viesbuciai/accounts/profile/')


@login_required(login_url="/viesbuciai/accounts/login/")
def make_reservation(request):
    """
    Rezervacijos view'sas.
    :param request: automatinė užklausa.
    :return: rodoma viešbučių rezervacijos forma.
    Neradus viešbučio - grėžtama atgal.
    """
    if request.method == 'POST':

        form = OrderForm()
        hotel_id = request.POST.get('hotel')

        try:
            hotel = Hotel.objects.get(pk=hotel_id)
        except ObjectDoesNotExist:
            return redirect('hotels')

        balance = Balance.objects.select_related().get(user=request.user)

        context = {
            'hotel': hotel,
            'balance': round(balance.balance, 2),
            'form': form
        }

        return render(request, 'make_reservation.html', context=context)
    else:

        return redirect('hotels')


@login_required(login_url="/viesbuciai/accounts/login/")
def create_order(request, hotel_id):
    """
    Užsakymo kurimo view'sas.
    :param request: automatinė užklausa.
    :param hotel_id: būtinas viešbučio id.
    :return: viešbučio užsakymo užpildymo formos atvaizdavimas,
    balanco, neigiamų datų skirtumo patikra, hotelių prieinamumo skaičiavimas.
    Sėkmingu užklausos atveju nukreipiama į detales, arba grįžtama atgal.
    """
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():

            r_dates = form.cleaned_data.get('r_date')
            i_dates = form.cleaned_data.get('i_date')

            # Praejusu dienu pataisymas
            if r_dates < date.today() or i_dates < date.today():
                return redirect('hotels')

            days = (i_dates - r_dates).days

            balance = Balance.objects.select_related().get(user=request.user)
            order = form.save(commit=False)
            order.hotel = Hotel.objects.get(pk=hotel_id)
            order.user_id = request.user.id
            order.client = Profile.objects.get(user_id=request.user.id)

            # neigiamos dienos nepriimamos.
            if days == 0 or days < 0:
                return redirect('hotels')

            if balance.balance >= (days * order.hotel.price):
                balance.balance = balance.balance - (days * order.hotel.price)
                balance.save()

                order = form.save(commit=False)
                order.hotel = Hotel.objects.get(pk=hotel_id)

                hotel = Hotel.objects.get(id=hotel_id)

                hotel.availability = hotel.availability - 1
                hotel.save()
                order.save()

                return redirect('order_confirmation', order_id=order.id)
            else:
                return redirect('hotels')
        else:
            return redirect('hotels')
    else:
        return redirect('hotels')


@login_required(login_url="/viesbuciai/accounts/login/")
def order_confirmation(request, order_id):
    """
    Užsakymo patvirtinimo view'sas.
    :param request: automatinė užklausa.
    :param order_id: Būtinas užsakymo id.
    :return: Naudojamas tik sėkmingu atveju, kai create_order būna teisingas.
    """
    order = Order.objects.get(pk=order_id)
    return render(request, 'order_confirmation.html', {'order': order})


def my_orders(request):
    """
    Mano užsakymų view'sas.
    :param request: automatinė užklausa.
    :return: Rodomi užsakymai konkretaus pirkėjo, neprisijungus -
    nukreipimas į prisijungimo langą.
    """
    if request.user.is_authenticated:
        orders_ = Order.objects.filter(client=request.user.profile)
        return render(request, 'my_orders.html', {'orders': orders_})
    else:
        return redirect('login')


def orders(request):
    """
    Visų užsakymų view'sas
    :param request: automatinė užklausa.
    :return: rodomi visi užsakymai (tik su admin userio prieiga)
    """
    if request.user.is_authenticated:
        orders_ = Order.objects.all()
        return render(request, 'orders.html', {'orders_': orders_})
    else:
        return redirect('login')


@login_required(login_url="/viesbuciai/accounts/login/")
def edit_order(request, pk):
    """
    Užsakymo redagavimo view'sas.
    Prieiga tik admin useriui.
    :param request: aitomatinė užklausa
    :param pk: užsakymo id.
    :return: admin detalių pridėjimas prie esamų užsakymų.
    """
    order = Order.objects.get(pk=pk)
    admin_details = AdminDetails.objects.get(order=order)
    if request.method == 'POST':
        form = EditOrderForm(request.POST, instance=order)
        admin_details_form = EditAdminDetailsForm(request.POST, instance=admin_details)
        if form.is_valid() and admin_details_form.is_valid():
            form.save()
            admin_details_form.save()
            return redirect('orders_')
    else:
        form = EditOrderForm(instance=order)
        admin_details_form = EditAdminDetailsForm(instance=admin_details)
    context = {'form': form, 'admin_details_form': admin_details_form}
    return render(request, 'edit_order.html', context)


@login_required(login_url="/viesbuciai/accounts/login/")
def hotel_filter(request):

    """
    Viešbučių filtravimo paieška pagal viešbučio pavadimą,
    reitingą ir max žmonių kiekį.
    """

    profile_ = Profile.objects.get(user=request.user)
    if profile_.name and profile_.lastname and profile_.address and \
            profile_.birth_date and profile_.city and profile_.country:

        hotels_ = Hotel.objects.all()
        name = request.GET.get('name')

        if name:
            hotels_ = hotels_.filter(name__iexact=name)
        stars = request.GET.get('stars')
        if stars:
            hotels_ = hotels_.filter(stars=stars)
        quantity = request.GET.get('quantity')
        if quantity:
            hotels_ = hotels_.filter(quantity=quantity)

        context = {'hotels': hotels_}

        # naujas vartotojas neturi balanso -  taisom.

        try:
            balance = Balance.objects.get(user=request.user)
            rounded = round(balance.balance, 2)
            context['balance'] = rounded
        except ObjectDoesNotExist:
            context['balance'] = 0

        #####################################

        return render(request, 'hotel_filter.html', context)

    else:

        return HttpResponseRedirect('/viesbuciai/accounts/profile/')


@login_required(login_url="/viesbuciai/accounts/login/")
def add_user_balance_view(request, user_id):
    """
    Balanco pridėjimo view'sas.
    :param request: automatinė užklausa
    :param user_id: vartotojo id
    :return: Jeigu balancas nėra neigiamas arba neteisingu formatu,
    pridedamas balancas.
    """

    # Naujas vartotojas neturi balanso - taisom crash.
    try:
        balance = Balance.objects.select_related().get(user=user_id)
    except ObjectDoesNotExist:
        user = User.objects.get(id=user_id)
        balance = Balance.objects.create(user=user, balance=0)
        balance.save()
    #########################################

    if request.method == 'POST':

        try:
            amount = float(request.POST.get('amount'))
        except ValueError:
            pass

        try:
            if not amount < 0:
                balance.balance = amount
                balance.save()
        except UnboundLocalError:
            pass

        return redirect('all_users')

    return render(request, 'add_user_balance.html')


@login_required(login_url="/viesbuciai/accounts/login/")
def all_users_view(request):
    """
    Visu vartotoju peržiūros view'sas.
    Prieiga tik admin useriui.
    """
    users = User.objects.all()
    context = {'users': []}
    for user in users:
        try:
            balance = Balance.objects.get(user=user)
            profile_ = Profile.objects.get(user=user)
            context['users'].append({'user': user, 'balance': round(balance.balance, 2), 'profile': profile_})
        except ObjectDoesNotExist:
            profile_ = Profile.objects.get(user=user)
            context['users'].append({'user': user, 'balance': None, 'profile': profile_})
    return render(request, 'all_users.html', context)


@login_required(login_url="/viesbuciai/accounts/login/")
def add_hotel_view(request):
    """
    Naujo viešbučio sukūrimas.
    Prieiga tik admin useriui.
    """
    if request.method == 'POST':
        form = HotelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hotel_filter')
        else:
            form = HotelForm()
        return render(request, 'add_hotel.html', {'form': form})
    else:
        form = HotelForm()
        return render(request, 'add_hotel.html', {'form': form})


@login_required(login_url="/viesbuciai/accounts/login/")
def delete_hotel(request, pk):
    """
    Viešbučio ištrynimas.
    Ištrinama tik tuo atveju, jeigu su esamu viešbučiu nėra užsakymų.
    Prieiga tik admin useriui.
    """
    if request.method == 'POST':
        hotel = Hotel.objects.get(pk=pk)
        # Neleidziam trinti su uzsakymo objektais, nes galimi crash'ai.
        if not Order.objects.filter(hotel=hotel).exists():
            hotel.delete()
            return redirect('hotel_filter')
        else:
            return redirect('hotel_filter')
    else:
        return render(request, 'hotel_confirm_delete.html', {'pk': pk})
