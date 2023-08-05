import json
import pathlib as pl
from typing import Callable, List, Union

from p4x.laboratory.experiments import (
    exception as _exception,
    project as _project,
)

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"


class Manager(object):
    _projects: List['_project.Project'] = []

    def __init__(self):
        pass

    @property
    def projects(self):
        return self._projects

    @projects.setter
    def projects(self, projects: List['_projects.Project']):
        self._projects = list(set(projects))

    @projects.deleter
    def projects(self):
        del self._projects

    def load(self, path: Union[str, pl.Path]):
        # make sure we have a `pathlib.Path` object
        path = pl.Path(path).resolve()

        # read file
        try:
            # import the object schemes
            import p4x.laboratory.experiments.marshmallow

            # load JSON data from file into a regular python dictionary
            data = json.loads(path.read_text())

            # and parse the data as well as convert it into the correct objects
            self.projects = p4x.laboratory.experiments.marshmallow.ProjectSchema(
                    many=True).load(data)
            return self.projects
        except FileNotFoundError:
            return []

    def save(self, path: Union[str, pl.Path], *args, **kwargs):
        # make sure we have a `pathlib.Path` object
        path = pl.Path(path).resolve()

        # import schema dumper
        import p4x.laboratory.experiments.marshmallow

        # write file with data dumped from python objects into a regular
        # python dictionary
        path.write_text(json.dumps(
                p4x.laboratory.experiments.marshmallow.ProjectSchema(
                        many=True).dump(self.projects), **kwargs))

    def find(self, name: str, fltr: Callable = None):
        # default filter is to filter by name
        if fltr is None:
            def fltr(project):
                return name == project.name

        # search for the project by name
        found = [project for project in self.projects if fltr(project)]

        # found one, then return that
        if len(found) == 1:
            return found[0]
        # found more than one, then return a project not found error message
        # stating how many projects we found
        elif len(found) > 1:
            raise _exception.ProjectNotFoundError(
                    'Search clause ambiguous. Found {} projects that match the '
                    'name `{}`:\n  {:s}'.format(
                            len(found),
                            name,
                            "\n  ".join([project.name for project in found])))
        # no match
        else:
            # to find projects with a name similar to the searched one,
            # we will use `difflib`
            import difflib

            closest = difflib.get_close_matches(name,
                                                [project.name for project in
                                                 self.projects],
                                                n=len(self.projects),
                                                cutoff=0.3)
            # if closest matches were found, we will display them nicely to
            # the user
            if len(closest):
                # to align the names correctly in the error message, we will
                # count the longest entry
                longest = len(max(closest, key=len))

                raise _exception.ProjectNotFoundError(
                        'No unique match found. However, the following '
                        'projects have very similar names:\n{}'.format(
                                (('{{:>{}}}\n'.format(longest + 2)) * len(
                                        closest)).format(*closest)))
            # no closest matches were found, we will bail out with a simple
            # not found error
            else:
                raise _exception.ProjectNotFoundError(
                        'No project found with name `{}` found and also no '
                        'similarly named projects.'.format(name))


__all__ = [
        'Manager',
]
