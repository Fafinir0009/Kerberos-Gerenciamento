from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms.FormPet import PetForm
from ..models.pet import Pet

def listar_pets(request):
    pets = Pet.objects.all()
    return render(request, 'pet/pets.html', {'pets': pets})

def criar_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pet cadastrado com sucesso!')
            return redirect('pets')
    else:
        form = PetForm()
    return render(request, 'pet/form_pet.html', {'form': form})

def editar_pet(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pet atualizado com sucesso!')
            return redirect('lista_pets')
    else:
        form = PetForm(instance=pet)
    return render(request, 'pet/pet_form.html', {'form': form})

def deletar_pet(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if request.method == 'POST':
        pet.delete()
        messages.success(request, 'Pet removido com sucesso!')
        return redirect('pets')
    return render(request, 'pet/pet_deletar.html', {'pet': pet})