{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. :exclude-members: set_shortcuts_to_canvas, to_dict, to_kwargs, update, update_from_dict

.. autoclass:: {{ objname }}

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

.. include:: {{module}}.{{objname}}.examples

.. raw:: html

    <div style='clear:both'></div>