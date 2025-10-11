{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :exclude-members: __init__, set_shortcuts_to_canvas, to_dict, to_kwargs, update, update_from_dict, describe_tree

   {% block methods %}

   {% if methods %}
   .. rubric:: Methods

   .. autosummary::
      :toctree: {{ objname }}
   {% for item in methods %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

{% if gallery_enabled %}
.. include:: {{module}}.{{objname}}.examples.rst
.. raw:: html

    <div style='clear:both'></div>
{% endif %}
