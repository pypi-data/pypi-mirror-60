#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=2.7
# license         :GPLv3
# ==============================================================================

# Import
import pywdpa


# test_get_token
def test_get_token():
  token = pywdpa.get_token(key="")
  r = ["\nMissing WDPA API token. Please ensure that:\n",
       "1) You completed this form [https://api.protectedplanet.net/request] to get the token,\n",
       "2) You stored the value as an environment variable with the recommended name WDPA_KEY."]
  assert token == "".join(r)

# End
