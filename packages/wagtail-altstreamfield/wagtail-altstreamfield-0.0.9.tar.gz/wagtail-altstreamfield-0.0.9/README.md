# Wagtail AlternateStreamField


This project provides an alternate implementation of Wagtail's StreamField.
This was created to resolve issues with performance for more complicated block structures.

## Basic Installation and Usage

To install use pip:

`pip install wagtail-altstreamfield`

Add "altstreamfield" to your Django Project's `INSTALLED_APPS` list.

Create some custom blocks and a `wagtail.core.models.Page` subclass like the following:

```python
#filename: [yourapp]/models.py
from django.db import models

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel

from altstreamfield.edit_handlers import AltStreamFieldPanel
from altstreamfield.fields import AltStreamField

from altstreamfield.blocks import (
    StreamBlock,
    StructBlock,

    BooleanField,
    CharField,
    ChoiceField,
    DocumentChooserField,
    ImageChooserField,
    IntegerField,
    RichTextField,
    StreamBlockField,
    TextField,
)

# Create some custom blocks
HEADING_TYPE_CHOICES = (
    ('h1', 'H1'),
    ('h2', 'H2'),
    ('h3', 'H3'),
    ('h4', 'H4'),
    ('h5', 'H5'),
    ('h6', 'H6'),
)

class Heading(StructBlock):
    heading_type = ChoiceField(choices=HEADING_TYPE_CHOICES, required=True)
    text = CharField()

    class Meta:
        icon = 'title'


class Paragraph(StructBlock):
    text = RichTextField()

    class Meta:
        icon = 'pilcrow'


class DocumentLink(StructBlock):
    title = CharField()
    document = DocumentChooserField()

    class Meta:
        icon = 'doc-empty'


class SimpleStreamBlock(StreamBlock):
    heading = Heading()
    paragraph = Paragraph()
    document = DocumentLink()


# Create your models here.
class HomePage(Page):
    body = AltStreamField(SimpleStreamBlock)

    content_panels = Page.content_panels + [
        AltStreamFieldPanel('body', classname='full'),
    ]
```

If you are creating a large number of blocks it is a good idea to separate the blocks into a separate module or modules.
