from django import forms
from .models import Project, Task, Comment, Label


class BootstrapFormMixin:
    def _bootstrap(self):
        for _, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput)):
                cls = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (cls + " form-control").strip()
        return self


class ProjectForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap()


class TaskForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "priority", "due_date", "labels"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)
        if owner is not None:
            self.fields["labels"].queryset = Label.objects.filter(owner=owner)
        self.fields["labels"].widget.attrs["class"] = "form-select"
        self._bootstrap()


class LabelForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Label
        fields = ["name", "color"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap()


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 2, "placeholder": "Напишіть коментар..."})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap()
