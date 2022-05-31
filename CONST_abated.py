import logging


# Whoops. Too lax(ative) with the syntax.
class CONSTAbatedException(Exception):
    UNEXPECTED_OBJECT_TYPE_GOT_S = "Unexpected object type. Need dictionary, got %s."


def __populate_object(const_object, values):
    if isinstance(values, dict):
        for var, val in values.items():
            logging.debug("setting variable %s" % var)
            setattr(const_object, var, val)
    else:
        raise CONSTAbatedException(
            CONSTAbatedException.UNEXPECTED_OBJECT_TYPE_GOT_S % type(values)
        )


def load_from_yaml(yaml_configuration_file, const_object):
    import yaml

    try:
        fin = open(yaml_configuration_file, "r")
        raw_yaml = fin.read()
        fin.close()
        __populate_object(const_object, yaml.load(raw_yaml))
    except IOError as e:
        logging.error(
            "Could not open config file %s. Bailing out." % yaml_configuration_file
        )
        raise e
    except yaml.scanner.ScannerError as e:
        logging.error("Syntax error in %s. Bailing out." % yaml_configuration_file)
        raise e


# TODO: load_from_json
