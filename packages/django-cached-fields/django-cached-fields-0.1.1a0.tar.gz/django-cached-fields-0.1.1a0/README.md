# django-cached-fields
Cached fields for Django

## Usage

Defining a basic Cached Field

The first argument of the CachedField constructor can be the name of a method on the class.

This method only works with field triggers as signal triggers will require a `CachedFieldSignalHandler`.
```python
class Invoice(models.Model):
    name = models.TextField(null=False)
    quantity = models.IntegerField()
    amount = models.IntegerField(null=False)

    def calc_total(self):
        self.total = self.quantity * self.amount

    total = CachedIntegerField(
        'calc_total', 
        field_triggers=[
            'amount',
        ],
        timeout=timedelta(seconds=5),
    )
```

If you would like your cached field's callback to be triggered by a signal, you will need to create a signal handler.
```python
class InvoiceSignalHandler(CachedFieldSignalHandler):
    
    def calc_total(instance):
        instance.total = instance.quantity * instance.amount

    @for_class('Customer')
    def cutomer_total(customer):
        return invoice.quantity * invoice.amount

    @for_class('Supplier')
    def supplier_total(supplier):
        invoice = supplier.invoice.last()
        return invoice.quantity * invoice.amount

```

If you would like to offload task processing to Celery, django-cached-fields can handle that for you automatically.

`settings.py`
```python

CACHED_FIELDS_CELERY_ENABLED = True
CACHED_FIELDS_CELERY = {
    "queue": "default"
}

```

If you'd like to offload a recalculation to a specific queue, you can do this.

```python
class InvoiceSignalHandler(CachedFieldSignalHandler):
    
    def calc_total(instance):
        instance.total = instance.quantity * instance.amount

    @for_class('Customer', queue="low_priority")
    def cutomer_total(customer):
        invoices = customer.invoices.all()
        for i in invoices:
            i.cache_toolkit.update_cache('total', i.quantity * i.amount)
            i.save()

    @for_class('Supplier')
    def supplier_total(supplier):
        invoice = supplier.invoice.last()
        invoice.total = invoice.quantity * invoice.amount

```

Force Recalculation
```python

ym = YourModel.objects.create(name="fart", amount=6)

ym.cache_toolchain.refresh_field('total')

```

Get last time the cache was updated

<br>
For when you need to run queries
```python
In [2]: print(ym.total_last_update)
Out[2]: datetime.datetime(2019,10,30,4,30,54)

In [3]: YourModel.objcts.filter(total_last_update__date__gte=date(2019,10,1)).exists()
Out[3]: True
```