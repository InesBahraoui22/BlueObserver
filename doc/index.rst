.. test documentation master file, created by
   sphinx-quickstart on Fri Nov 28 09:13:12 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

hello.rst

BlueObserver Documentation
==================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.

**Mensual and configurated for physical limiting parameters map of marine mammals observations in Northern Europe**

Introduction
============
.. toctree::
   :maxdepth: 2 
   :caption: Contents:

BlueObserver is a scientifical pipeline that has been produced to collect, enrich
and visualise observational data of marine mammals thanks to multiple sources (OBIS, Copernicus Marine, Open-Meteo).
This is to be used by curious, environmentally-friendly travelers that seek to watch marine mammals
with respects to European policies regarding the animal well-being.

Main fonctionnalities
---------------------------
* Recovery of species observations via the API OBIS
* Implementation of the marine conditions (Copernicus Marine)
* Combination of the meteorological data (Open-Meteo)
* Creation of the complete dataset for visualisation
* Interactive Web interface using Flask

Quick Install
===================

.. code-block:: bash

   git clone https://github.com/InesBahraoui22/BlueObserver.git
   cd BlueObserver
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate sur Windows
   pip install -r requirements.txt

User guide book
===================

See main README for additional details on the executing of the pipeline.

.. toctree::
   :hidden:
   
   introduction
   installation
   usage
   api/modules
   contributing



