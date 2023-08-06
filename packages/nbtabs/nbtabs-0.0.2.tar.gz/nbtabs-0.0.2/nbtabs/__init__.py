import jupytext
import argh

from jinja2 import Template
from nbformat import NotebookNode 
from copy import copy, deepcopy

__version__ = "0.0.2"


TAB_NAV_TEMPLATE = """
<!--html_preserve-->
<div class="tabs">
  <ul class="nav nav-tabs">   
    {%- for tab in tabs -%}
      <li>
        <a class="{{tab.pytabs.class}} {{ 'tabs__link--active' if loop.first }}" href="#{{ tab.cell_id }}">{{tab.pytabs.name}}</a>
      </li>
    {%- endfor -%}
  </ul>
</div>
<!--/html_preserve-->

"""

# Util funcs ------------------------------------------------------------------

def get_pytab_cells_dict(cells):
    res = {}
    for cell in cells:
        meta = get_pytab_meta(cell)

        if meta is not None:
            # danger: could have duplicate class entries
            class_key = meta["class"]
            res[class_key] = cell

    return res


def enum_pytab_cells(cells):
    for ii, cell in enumerate(cells):
        if is_pytab(cell):
            yield ii, cell


def get_pytab_meta(cell):
    return getattr(cell.metadata, 'pytabs', None)


def create_pytab_cell_id(meta):
    return meta.pytabs["class"] + "--" + meta.pytabs["name"].replace(" ", "-").lower()

def create_node_with_id(cell):
    out = deepcopy(cell)
    out.metadata["cell_id"] = create_pytab_cell_id(out.metadata)

    return out


def is_pytab(cell):
    return get_pytab_meta(cell) is not None


def process_other_cell(cell_dict, tab_class):
    # TODO: handle case where no matching cell
    cell = cell_dict.get(tab_class)
    return create_node_with_id(cell)


# Main entry point funcs ------------------------------------------------------

def pytabs_create_cells(main_name, other_names = tuple()):
    tab_nav_template = Template(TAB_NAV_TEMPLATE)

    nb1 = jupytext.read(main_name) if isinstance(main_name, str) else main_name
    other_nbs = [jupytext.read(fname) for fname in other_names]
    other_nb_cells = [get_pytab_cells_dict(nb.cells) for nb in other_nbs]


    # collect cells from other notebooks
    #   - main notebook will have meta.pytabs.class
    #   - other notebooks will have matching cells
    # need index from main notebook for next step
    
    # result should be a list of cells (first being a nav list)
    pytab_cells = {}
    for nb1_indx, cell in enum_pytab_cells(nb1.cells):
        tab_class = cell.metadata["pytabs"]["class"]

        # add cell ids
        new_cell = create_node_with_id(cell)

        other_cells = [process_other_cell(cell_dict, tab_class) for cell_dict in other_nb_cells]
        other_cell_meta = [cell.metadata for cell in other_cells]


        # run template ------------
        nav_cell = NotebookNode(
                cell_type = 'markdown',
                metadata = NotebookNode(),
                source = tab_nav_template.render(tabs = [new_cell.metadata, *other_cell_meta])
                )

        # output list of cells -------
        pytab_cells[nb1_indx] = [nav_cell, new_cell, *other_cells]
    return pytab_cells


def pytabs_insert_cells(notebook, tab_cells):
  # identify where navlist needs to be inserted, do ittttt
  final_cells = []
  prev_ii = 0
  for ii, cell_list in tab_cells.items():
      prev_cells = notebook.cells[prev_ii:ii]
      final_cells.extend([*prev_cells, *cell_list])
  
      prev_ii = ii + 1
  
  final_cells.extend(notebook.cells[prev_ii:])
  
  final_nb = copy(notebook)
  final_nb['cells'] = final_cells

  return final_nb

# CLI -------------------------------------------------------------------------

import shutil
from pathlib import Path
from pkg_resources import resource_filename

@argh.arg("other_names", nargs = "+")
def convert(main_name, other_names, out_name = None, execute = False):
    """Convert a main notebook, to include tabbed cells based on other notebooks."""
    nb1 = jupytext.read(main_name)
    tab_cells = pytabs_create_cells(nb1, other_names)
    final_nb = pytabs_insert_cells(nb1, tab_cells)

    if out_name is None:
        *name, ext = main_name.split('.')
        out_name = "{}-tabbed.{}".format(".".join(name), ext)

    if execute:
        from nbconvert.preprocessors import ExecutePreprocessor
        path = str(Path(main_name).parent)
        ep = ExecutePreprocessor(timeout=600)
        ep.preprocess(final_nb, {'metadata': {'path': path}})

    jupytext.write(final_nb, out_name)

def setup():
    """Copy templates to one of the nbconvert directories."""
    from jupyter_core.paths import jupyter_path 

    template_path = Path(resource_filename('nbtabs', 'templates'))
    paths = jupyter_path()

    print("Possible paths:")
    print("\n".join("%s: %s" %(ii, path) for ii, path in enumerate(paths)))
    path_indx = input("Select path: ").strip()

    dst_path = Path(paths[int(path_indx)]) / 'nbconvert' / 'templates' / 'html'
    for src_fname in template_path.glob("*tpl"):
        shutil.copy2(src_fname, dst_path / src_fname.name)


def copy_templates(dst_dir):
    """Copy templates and assets to dst_dir."""
    template_path = Path(resource_filename('nbtabs', 'templates'))
    shutil.copytree(template_path, dst_dir)


def main():
    argh.dispatch_commands([convert, setup, copy_templates])



if __name__ == "__main__":
    main()

