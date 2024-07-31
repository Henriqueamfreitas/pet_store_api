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
        trait_param = request.query_params.get("trait", None)
        if trait_param is not None:
            pets = Pet.objects.filter(traits__name=trait_param)
        else:
            pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets, request, view=self)
        pets_serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(pets_serializer.data)


class PetDetailView(APIView):
    def get(self, request, pet_id):
        filtered_pet = Pet.objects.filter(id=pet_id)
        pet_serializer = PetSerializer(filtered_pet[0])
        return Response(pet_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pet_id):
        try:
            Pet.objects.get(pk=pet_id).delete()
        except Pet.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pet_id):
        try:
            pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status.HTTP_404_NOT_FOUND,
            )
        pet_serializer = PetSerializer(data=request.data, partial=True)
        if pet_serializer.is_valid() is False:
            return Response(
                pet_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        request_keys = list(pet_serializer.validated_data.keys())

        sum_group = 0
        sum_traits = 0
        for key in request_keys:
            if key == "group":
                sum_group += 1
            if key == "traits":
                sum_traits += 1
        if sum_group > 0:
            request_keys.remove("group")
            group = pet_serializer.validated_data["group"]
            filtered_group = Group.objects.filter(
                scientific_name=group["scientific_name"]
            )
            if filtered_group.count() == 0:
                new_group = Group.objects.create(**group)
            new_group = filtered_group[0]
            setattr(pet, "group", new_group)

        if sum_traits > 0:
            request_keys.remove("traits")
            traits = pet_serializer.validated_data["traits"]
            traits_list = []
            for i in range(0, len(traits)):
                filtered_trait = Trait.objects.filter(name__iexact=traits[i]["name"])

                if filtered_trait.count() == 0:
                    new_trait = Trait.objects.create(**traits[i])
                    traits_list.append(new_trait)
                else:
                    traits_list.append(filtered_trait[0])
            pet.traits.set(traits_list)

        request_values = list(pet_serializer.validated_data.values())
        for i in range(0, len(request_keys)):
            setattr(pet, request_keys[i], request_values[i])

        pet.save()
        pet_serializer = PetSerializer(pet)
        return Response(pet_serializer.data, status=status.HTTP_200_OK)
