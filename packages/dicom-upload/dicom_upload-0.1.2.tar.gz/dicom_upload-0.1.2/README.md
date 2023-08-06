# dicom-upload

[![Build Status](https://travis-ci.org/jsc/dicom-upload.svg?branch=master)](https://travis-ci.org/jsc/dicom_upload)
[![codecov](https://codecov.io/gh/jsc/dicom-upload/branch/master/graph/badge.svg)](https://codecov.io/gh/jsc/dicom-upload)


FileUpload Widget using the Jupyter Notebook Server RestAPI.
Uploads DICOM files with anonymized headers, i.d. the 0004 and 
0010 tags are removed on JS side before the upload.

Can handle large files by uploading files in chunks.

## Installation

You can install using `pip`:

```bash
pip install dicom_upload
```
or from this GitLab directly

```bash
pip install git+https://gitlab.version.fz-juelich.de/jupyter4jsc/j4j_extras/dicom-upload.git
```

Or if you use jupyterlab:

```bash
pip install dicom_upload
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:
```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] dicom_upload
```
