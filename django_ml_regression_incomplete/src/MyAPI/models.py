from django.db import models

# Create your models here.


class approvals(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    MARRIED_CHOICES = (
    ('Yes', 'Yes'),
    ('No', 'No')
    )
    GRADUATED_CHOICES = (
    ('Graduate', 'Graduated'),
    ('Not_Graduate', 'Not_Graduate')
    )
    SELFEMPLOYED_CHOICES = (
    ('Yes', 'Yes'),
    ('No', 'No')
    )
    PROPERTY_CHOICES = (
    ('Rural', 'Rural'),
    ('Semiurban', 'Semiurban'),
    ('Urban', 'Urban')
    )

    firstname = models.CharField(max_length=15)
    lastname = models.CharField(max_length=15)
    dependants = models.IntegerField()
    applicantincome = models.IntegerField()
    coApplicantincome = models.IntegerField()
    loanAmt = models.IntegerField()
    loanTerm = models.IntegerField()
    credithistory = models.IntegerField()
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES)
    married = models.CharField(max_length=15, choices=MARRIED_CHOICES)
    graduateEducation = models.CharField(max_length=15, choices=GRADUATED_CHOICES)
    selfEmployed = models.CharField(max_length=15, choices=SELFEMPLOYED_CHOICES)
    area = models.CharField(max_length=15, choices=PROPERTY_CHOICES)

    def __str__(self):
        return '{}, {}'.format(self.lastname, self.firstname)

    