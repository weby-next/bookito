from rest_framework import serializers
from ..models import Business
from rest_framework.exceptions import APIException


class SlugTakenError(APIException):
    status_code = 409
    default_code = "SLUG_TAKEN"
    default_detail = "Slug is already taken."


class BusinessWriteBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ("name", "slug", "description")
        # UniqueValidator خودکار را برمی‌داریم تا به‌جای ۴۰۹ خطای ۴۰۰ نگیریم
        extra_kwargs = {"slug": {"validators": []}}

    def validate_slug(self, value):
        value = value.lower()
        qs = Business.objects.filter(slug=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise SlugTakenError()
        return value


class BusinessCreateSerializer(BusinessWriteBaseSerializer):
    pass


class BusinessUpdateSerializer(BusinessWriteBaseSerializer):
    pass


class BusinessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = (
            "id",
            "name",
            "slug",
            "status",
            "created_at",
        )
        read_only_fields = fields


class BusinessDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class SlugAvailabilitySerializer(serializers.Serializer):
    slug = serializers.SlugField(max_length=100)
    business_id = serializers.IntegerField(required=False, min_value=1)

    def validate_slug(self, value):
        return value.lower()


class SlugAvailabilityResultSerializer(serializers.Serializer):
    slug = serializers.CharField()
    available = serializers.BooleanField()