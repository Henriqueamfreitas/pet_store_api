from rest_framework.views import APIView, status
from rest_framework.response import Response
from .models import Pet
from groups.models import Group
from traits.models import Trait
from .serializers import PetSerializer
from rest_framework.pagination import PageNumberPagination


class PetView(APIView, PageNumberPagination):
    def post(self, request):
        data = request.data
        pet_serializer = PetSerializer(data=data)
        if pet_serializer.is_valid() is False:
            return Response(
                pet_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        group = pet_serializer.validated_data["group"]
        filtered_group = Group.objects.filter(scientific_name=group["scientific_name"])
        if filtered_group.count() == 0:
            new_group = Group.objects.create(**group)
        new_group = filtered_group[0]
        new_pet = Pet.objects.create(
            name=pet_serializer.validated_data["name"],
            age=pet_serializer.validated_data["age"],
            weight=pet_serializer.validated_data["weight"],
            sex=pet_serializer.validated_data["sex"],
            group=new_group,
        )

        traits = pet_serializer.validated_data["traits"]
        for i in range(0, len(traits)):
            filtered_trait = Trait.objects.filter(name__iexact=traits[i]["name"])

            if filtered_trait.count() == 0:
                new_trait = Trait.objects.create(**traits[i])
                new_pet.traits.add(new_trait)
            else:
                new_pet.traits.add(filtered_trait[0])

        pet_serializer = PetSerializer(new_pet)

        return Response(pet_serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets, request, view=self)
        pets_serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(pets_serializer.data)
