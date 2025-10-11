{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autofunction:: {{ objname }}

{% if gallery_enabled %}
.. include:: {{module}}.{{objname}}.examples

.. raw:: html

    <div style='clear:both'></div>
{% endif %}

