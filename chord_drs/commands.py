import os
from typing import Optional
import click
from click import ClickException
from chord_drs.app import application, db
from chord_drs.models import DrsObject, DrsBundle


def create_drs_bundle(location: str, parent: Optional[DrsBundle] = None) -> DrsBundle:
    bundle = DrsBundle(name=os.path.basename(location))

    if parent:
        bundle.parent_bundle = parent

    for f in os.listdir(location):
        f = os.path.abspath(os.path.join(location, f))

        if os.path.isfile(f):
            create_drs_object(f, parent=bundle)
        else:
            create_drs_bundle(f, parent=bundle)

    bundle.update_checksum_and_size()
    db.session.add(bundle)

    print(f"Created a new bundle, name: {bundle.name}, ID : {bundle.id}, size: {bundle.size}")

    return bundle


def create_drs_object(location: str, parent: Optional[DrsBundle] = None):
    drs_object = DrsObject(location=location)

    if parent:
        drs_object.bundle = parent

    db.session.add(drs_object)

    print(f"Created a new object, filename: {drs_object.location} ID : {drs_object.id}")


@application.cli.command("ingest")
@click.argument("source")
def ingest(source: str):
    """
    When provided with a file or a directory, this command will add these
    to our list of objects, to be served by the application.

    Should we go through the directories recursively?
    """
    if os.path.exists(source):
        source = os.path.abspath(source)

        if os.path.isfile(source):
            create_drs_object(source)
        else:
            create_drs_bundle(source)

        db.session.commit()
    else:
        raise ClickException('File or directory provided does not exists')
