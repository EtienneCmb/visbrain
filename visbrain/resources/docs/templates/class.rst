{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

{% if module.startswith('visbrain.') %}
{% set parts = module.split('.') %}
{% if parts|length > 1 %}
{% set canonical_module = parts[0] ~ '.' ~ parts[1] %}
{% else %}
{% set canonical_module = module %}
{% endif %}
.. py:class:: {{ objname }}
   :module: {{ canonical_module }}
   :canonical: {{ canonical_module }}.{{ objname }}
   :noindex:

.. autoclass:: {{ objname }}
{% else %}
.. autoclass:: {{ objname }}
{% endif %}

   {% block methods %}
   {% endblock %}
