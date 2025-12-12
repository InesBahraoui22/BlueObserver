Installation
==============

Prerequisites
--------------

* Python 3.8 or up
* pip (Python packages gestionary)

Dependencies installation
------------------------------

1. Cloning of the repository:

   .. code-block:: bash

      git clone https://github.com/InesBahraoui22/BlueObserver.git
      cd BlueObserver

2. Creation of a virtual environment (recommanded):

   .. code-block:: bash
      :caption: Windows

      python -m venv venv
      venv\Scripts\activate

   .. code-block:: bash
      :caption: macOS/Linux

      python -m venv venv
      source venv/bin/activate

3. Dependencies installation:

   .. code-block:: bash

      pip install -r requirements.txt

APIs configuration
------------------------

* **Copernicus Marine** : Create a free account on `marine.copernicus.eu`
* **Open-Meteo** : No API key needed to use the archive API

Installation verification
------------------------------

Test that everyting is working smoothly:

.. code-block:: bash

   python -c "import pandas; print('Pandas OK')"
   python -c "import xarray; print('Xarray OK')"

To produce the documentation
---------------------------------------

.. code-block:: bash

   cd doc
   ./make.bat html  # Sur Windows
   # ou
   make html        # Sur Linux/macOS
