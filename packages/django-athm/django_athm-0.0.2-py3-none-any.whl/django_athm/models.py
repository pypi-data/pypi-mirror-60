import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import REFUND_URL, STATUS_URL
from .utils import get_http_adapter


class ATH_Transaction(models.Model):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REFUNDED = "REFUNDED"

    TRANSACTION_STATUS_CHOICES = [
        (PROCESSING, "processing"),
        (COMPLETED, "completed"),
        (REFUNDED, "refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(unique=True, max_length=64)
    status = models.CharField(
        max_length=16, choices=TRANSACTION_STATUS_CHOICES, default=PROCESSING
    )

    # TODO: Use ATH's date
    date = models.DateTimeField(auto_now_add=True)

    total = models.FloatField()
    tax = models.FloatField(null=True)
    refunded_amount = models.FloatField(null=True)
    subtotal = models.FloatField(null=True)

    metadata_1 = models.CharField(max_length=64, null=True)
    metadata_2 = models.CharField(max_length=64, null=True)

    class Meta:
        verbose_name = _("ATH transaction")
        verbose_name_plural = _("ATH transactions")

    def __str__(self):
        return self.reference_number

    http_adapter = get_http_adapter()

    @classmethod
    def refund(cls, transaction, amount=None):
        # Refund the whole transaction by default
        if not amount:
            amount = transaction.total

        response = cls.http_adapter.post(
            REFUND_URL,
            data=dict(
                publicToken=settings.DJANGO_ATHM_PUBLIC_TOKEN,
                privateToken=settings.DJANGO_ATHM_PRIVATE_TOKEN,
                referenceNumber=transaction.reference_number,
                amount=str(amount),
            ),
        )

        if "errorCode" in response:
            raise Exception(response.get("description"))

        # Update the transaction status if refund was successful
        if response["refundStatus"] == "completed":
            transaction.status = cls.REFUNDED
            transaction.refunded_amount = response["refundedAmount"]
            transaction.save()

        return response

    @classmethod
    def inspect(cls, transaction):
        response = cls.http_adapter.post(
            STATUS_URL,
            data=dict(
                publicToken=settings.ATHM_PUBLIC_TOKEN,
                privateToken=settings.ATHM_PRIVATE_TOKEN,
                referenceNumber=transaction.reference_number,
            ),
        )

        return response


class ATH_Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(ATH_Transaction, on_delete=models.CASCADE)

    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    quantity = models.PositiveSmallIntegerField(default=1)

    price = models.FloatField()
    tax = models.FloatField(null=True)
    metadata = models.CharField(max_length=64, null=True)

    class Meta:
        verbose_name = _("ATH item")
        verbose_name_plural = _("ATH items")

    def __str__(self):
        return self.name
