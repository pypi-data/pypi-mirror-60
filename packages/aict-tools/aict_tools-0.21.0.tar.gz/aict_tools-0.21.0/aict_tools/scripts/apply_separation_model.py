import click
from tqdm import tqdm
import pandas as pd

from ..apply import predict_separator
from ..io import (
    append_column_to_hdf5,
    read_telescope_data_chunked,
    drop_prediction_column,
    load_model,
)
from ..configuration import AICTConfig
from ..logging import setup_logging


@click.command()
@click.argument('configuration_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('data_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('model_path', type=click.Path(exists=True, dir_okay=False))
@click.option('-v', '--verbose', help='Verbose log output', is_flag=True)
@click.option(
    '-N', '--chunksize', type=int,
    help='If given, only process the given number of events at once'
)
@click.option('-y', '--yes', help='Do not prompt for overwrites', is_flag=True)
def main(configuration_path, data_path, model_path, chunksize, yes, verbose):
    '''
    Apply loaded model to data.

    CONFIGURATION_PATH: Path to the config yaml file.
    DATA_PATH: path to the FACT/CTA data.
    MODEL_PATH: Path to the pickled model.

    The program adds the following columns to the inputfile:
        `output_name`: the output of model.predict_proba for the
        class name given in the config file.

    If `output_name` is not given in the config file,
    the default value of "gamma_prediction" will be used.
    '''
    log = setup_logging(verbose=verbose)

    config = AICTConfig.from_yaml(configuration_path)
    model_config = config.separator

    prediction_column_name = model_config.output_name
    drop_prediction_column(
        data_path, group_name=config.telescope_events_key,
        column_name=prediction_column_name, yes=yes
    )
    if config.has_multiple_telescopes:
        drop_prediction_column(
            data_path, group_name=config.array_events_key,
            column_name=prediction_column_name, yes=yes
        )

    log.debug('Loading model')
    model = load_model(model_path)
    log.debug('Loaded model')

    df_generator = read_telescope_data_chunked(
        data_path, config, chunksize, model_config.columns_to_read_apply,
        feature_generation_config=model_config.feature_generation
    )

    if config.has_multiple_telescopes:
        chunked_frames = []

    table = config.telescope_events_key
    for df_data, start, stop in tqdm(df_generator):

        prediction = predict_separator(df_data[model_config.features], model)

        if config.has_multiple_telescopes:
            d = df_data[['run_id', 'array_event_id']].copy()
            d[prediction_column_name] = prediction
            chunked_frames.append(d)

        append_column_to_hdf5(data_path, prediction, table, prediction_column_name)

    # combine predictions
    if config.has_multiple_telescopes:
        array_table = config.array_events_key
        d = pd.concat(chunked_frames).groupby(
            ['run_id', 'array_event_id'], sort=False
        ).agg(['mean', 'std'])
        mean = d[prediction_column_name]['mean'].values
        std = d[prediction_column_name]['std'].values

        append_column_to_hdf5(
            data_path, mean, array_table, prediction_column_name + '_mean'
        )
        append_column_to_hdf5(
            data_path, std, array_table, prediction_column_name + '_std'
        )


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
