from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from accounts.models import CustomUser

class UserCreationForm(forms.ModelForm):
    """
    Formulaire pour créer un nouvel utilisateur via l'admin.
    """
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmer le mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'permission')

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """
    Formulaire pour mettre à jour un utilisateur via l'admin.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'permission')
