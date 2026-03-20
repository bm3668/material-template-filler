#!/usr/bin/env python3
import sys
import os
import glob

sys.path.insert(0, '.')

from fill_from_inputs import main

# 找到文件
input_files = glob.glob('/home/admin/.openclaw/workspace/inputs/*.docx')
template_files = glob.glob('/home/admin/.openclaw/workspace/templates/*.docx')

if not input_files:
    print("❌ 未找到项目说明文档")
    sys.exit(1)

if not template_files:
    print("❌ 未找到模板文件")
    sys.exit(1)

template = template_files[0]
input_doc = input_files[0]

print(f"模板：{template}")
print(f"项目说明：{input_doc}")
print()

sys.argv = ['fill_from_inputs.py', template, input_doc]
main()
