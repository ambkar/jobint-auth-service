from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, null=True)
    surname = fields.CharField(max_length=100, null=True)
    phone = fields.CharField(max_length=20, unique=True, null=False)
    avatar = fields.BinaryField(null=True)

    class Meta:
        table = "users"

class TempCode(models.Model):
    id = fields.IntField(pk=True)
    phone = fields.CharField(max_length=20)
    code = fields.CharField(max_length=10)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "temp_codes"
