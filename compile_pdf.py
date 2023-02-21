#!/usr/bin/python3

import os
import yaml
import jinja2
from pathlib import Path
from jinja2 import Template
# Setup our jinja environment so it doesn't conflict with LaTeX
latex_jinja_env = jinja2.Environment(
	block_start_string = '\BLOCK{',
	block_end_string = '}',
	variable_start_string = '\VAR{',
	variable_end_string = '}',
	comment_start_string = '\#{',
	comment_end_string = '}',
	line_statement_prefix = '%%',
	line_comment_prefix = '%#',
	trim_blocks = True,
	autoescape = False,
	loader = jinja2.FileSystemLoader(os.path.join(os.path.abspath('.'),"templates"))
)

hex_dir = "./hexes"
source_file = "adventure.tex"
main_template = "main.tex.j2"
hex_template = "hex_key.tex.j2"
# All hexes in the included hexes file will be compiled in the order they are listed
included_hexes_file = "included_hexes.yml"
tex_files = "./tex_files"

# Changes the file extension on a string to .tex.
def changeExtToTex(in_filename):
    filename = Path(in_filename)
    filename_wo_ext = filename.with_suffix('')
    filename_replace_ext = filename.with_suffix('.tex')
    return filename_replace_ext

#Imports the filename of a hex file and imports the hex variable
def importHex(filename):
    with open (filename, 'r') as f:
        hex = yaml.safe_load(f)['hex']
    return hex

# Create the tex file for a hex that can be imported into the main tex file
# Returns the name of the tex file it creates
def createHexTexFile(hex_filename, template_file, hex):
    template = latex_jinja_env.get_template(template_file)
    output_render = template.render(hex=hex)
    # The temporary tex files for each hex will be located in the tex files
    # directory and will have the same name as the yaml hex file. Just with a
    # tex extension
    output_file = os.path.join(tex_files,changeExtToTex(hex_filename))
    with open(output_file, "w") as f:
        f.write(output_render)

    return output_file

# Create the source document file from all jinja templates
def createSourceFile(main_template, hex_filenames, source_file):
    # Create all tex files for each hex and keep the names of all
    # files created in a list
    hex_tex_filenames = []
    for hex_filename in hex_filenames:
        # Import the file for each hex listed in included hexes
        hex = importHex(os.path.join(hex_dir,hex_filename))
        hex_tex_file = createHexTexFile(hex_filename, hex_template, hex)
        hex_tex_filenames.append(hex_tex_file)

    # Create the main source file, importing all tex hex files
    template = latex_jinja_env.get_template(main_template)
    output_render = template.render(hexes=hex_tex_filenames)
    with open(source_file, "w") as f:
        f.write(output_render)

def compilePDF(filename):
    os.system("pdflatex " + filename)

# Takes in a yaml file with variable "included_hexes" which includes a list of hex filenames
# Outputs the list of hex filenames for processing
def getIncludedHexes(filename):
    with open (filename, 'r') as f:
        hexes = yaml.safe_load(f)['included_hexes']

    return hexes

def main():
    hexes = getIncludedHexes(included_hexes_file)

    createSourceFile(main_template, hexes, source_file)
    # Compile the tex file into a pdf
    compilePDF(source_file)
    # Compile a second time so all the references are correctly generated
    compilePDF(source_file)
    
if __name__ == "__main__":
    main()
