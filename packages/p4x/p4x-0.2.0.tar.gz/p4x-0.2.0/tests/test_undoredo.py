import pathlib as pl

from p4x import undoredo


class UndoRedoTestSuite(object):

    def test_create_file(self, tmp_path: pl.Path):
        tmp_path = pl.Path('.').resolve() / 'file.txt'

        def create_file():
            tmp_path.touch()

        def unlink_file():
            tmp_path.unlink()

        def write_file_text():
            raise ValueError('invalid value')
            tmp_path.write_text('asd')

        def remove_file_text():
            tmp_path.write_text('')

        history = undoredo.History([
                undoredo.Command(create_file, unlink_file),
                undoredo.Command(write_file_text, remove_file_text)
        ])

        history.commit()
        history.rollback()
