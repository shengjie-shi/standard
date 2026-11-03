# -*- coding: utf-8 -*-
"""
Description:

@Author: ssjie

Created on: 2024/12/27
"""
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import (Any, Awaitable, Dict, Generic, Iterable, List, Literal,
                    Mapping, Optional, Tuple, TypeVar, Union, cast)


class SystemRequest(BaseModel):

    pass
