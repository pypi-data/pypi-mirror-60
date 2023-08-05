=====
Usage
=====

To use P4x in a project:

   .. code-block:: python

      import p4x

Color Schemes
-------------

I currently have two color schemes implemented which are derived from the corporate identities of two universities: my
former university, University of Stuttgart (UStutt), and my current university, Delft University of Technology (TU Delft).

These color schemes can be accessed via

   .. code-block:: python

      # TU Delft
      colors = p4x.colorschemes.TUDELFT
      # University of Stuttgart
      colors = p4x.colorschemes.USTUTT

A single color can be accessed via dictionary access like :code:`colors['cyan']`, which returns a :code:`Color` object.

