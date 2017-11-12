{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :special-members: __contains__,__getitem__,__iter__,__len__,__add__,__sub__,__mul__,__div__,__neg__,__hash__

   .. autosummary::
   {% for item in methods %}
      ~{{ name }}.{{ item }}
   {%- endfor %}

   {% block methods %}
   {% endblock %}