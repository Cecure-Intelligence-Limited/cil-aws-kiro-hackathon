#!/usr/bin/env python3
"""
Complete system test for Aura Desktop Assistant
Tests all components: backend, frontend, MCP, and integration
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Tuple

class AuraSystemTester:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.backend_dir = self.base_dir / "backend"
        self.results: List[Tuple[str, bool, str]] = [] 