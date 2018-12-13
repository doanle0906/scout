import logging
import click

from scout.parse.mme import phenotype_features, omim_disorders, genomic_features
from scout.utils.mme_query import send_request

LOG = logging.getLogger(__name__)

@click.command('hgnc', short_help='Check if a gene exist')
@click.option('--hgnc-symbol', '-s',
                help="A valid hgnc symbol",
)
@click.option('--hgnc-id', '-i',
                type=int,
                help="A valid hgnc id",
)
@click.option('--build', '-b',
                type=click.Choice(['37', '38']),
                default='37',
                help="Specify the genome build",
)
@click.pass_context
def hgnc(ctx, hgnc_symbol, hgnc_id, build):
    """
    Query the hgnc aliases
    """
    adapter = ctx.obj['adapter']

    if not (hgnc_symbol or hgnc_id):
        LOG.warning("Please provide a hgnc symbol or hgnc id")
        ctx.abort()

    if hgnc_id:
        result = adapter.hgnc_gene(hgnc_id, build=build)
        if result:
            hgnc_symbol = result['hgnc_symbol']
        else:
            LOG.warning("Gene with id %s could not be found", hgnc_id)
            ctx.abort()

    result = adapter.hgnc_genes(hgnc_symbol, build=build)

    if result.count() == 0:
        LOG.info("No results found")

    else:
        click.echo("#hgnc_id\thgnc_symbol\taliases\ttranscripts")
        for gene in result:
            click.echo("{0}\t{1}\t{2}\t{3}".format(
                gene['hgnc_id'],
                gene['hgnc_symbol'],
                ', '.join(gene['aliases']),
                ', '.join(tx['ensembl_transcript_id'] for tx in gene['transcripts']),
            ))



@click.command('matchmaker', short_help='Search for similar patients to a given one using MatchMaker Express')
@click.option('-case_id',
    type=click.STRING,
    nargs=1,
    required=True,
    help='id of a case',
)
@click.option('-patient',
    type=click.STRING,
    nargs=1,
    required=True,
    help='display name of a patient',
)
@click.option('-email',
    type=click.STRING,
    nargs=1,
    required=True,
    help='email of the scout user to include in MME contact info'
)
@click.option('-token',
    type=click.STRING,
    nargs=1,
    required=True,
    help='matchmaker authorization token',
)
@click.option('-mme_url',
    type=click.STRING,
    nargs=1,
    required=False,
    help='url of a running matchmaker instance',
    default='http://localhost:9020'
)
@click.option('-external',
    is_flag=True,
    default=False,
    help='query for similar patients inside or outside scout'
)
@click.option('-genes_only',
    is_flag=True,
    default=False,
    help='search for gene names, not variants'
)
@click.pass_context
def matchmaker(context, case_id, patient, email, token, mme_url, external, genes_only):
    """Query MatchMaker for patients similar to a given one

        Args:
            case_id(str): a scout case id
            patient(str): display name of a patient
            email(str): valid email of a scout user
            token(str): an access token recognized by MME server
            mme_url(str) : URL of the matchmaker instance the patients should be saved to.
                When this is provided the patients will be included in its database by sending a POST
                request to the server.
            external(bool flag): if the search should be performed on connected nodes
                                 or in scout patients in MME only
            genes_only(bool flag): if True only gene names will be part of genomic features of patients, not variants
    """
    LOG.info('MatchMaker patients query')

    # obtain MME patient ID from the provided info
    adapter = context.obj['adapter']
    case_obj = adapter.case(case_id)
    user_obj = adapter.user(email=email)
    if user_obj is None:
        LOG.info("could't find any user with email '{}' in scout database!".format(email))
        context.abort()
    contact_info = {
        'name' : user_obj['name'],
        'institution' : 'Clinical Genomics, SciLifeLab, Stockholm.',
        'href' : user_obj['email'],
    }

    if not case_obj:
        LOG.info("could't find a scout case with id '{}' in database".format(case_id))
        context.abort()

    ## re-create a json patient out of this scout individual:
    patient_obj = {}

    # retrieve the ID of the patients submitted to MME
    sex = None

    mme_patient_id = None
    for individual in case_obj['individuals']:
        if individual['display_name'] == patient:
            mme_patient_id = '.'.join([ case_obj['_id'], individual['individual_id'] ])
            if individual['sex'] == '1':
                sex = 'MALE'
            else:
                sex = 'FEMALE'

    if not mme_patient_id:
        LOG.info("could't find patient '{}' in scout case with id {}".format(patient, case_id))
        context.abort()

    patient_obj['id'] = mme_patient_id
    patient_obj['contact'] = contact_info

    # collect HPO phenotype terms (if available) for this case
    patient_obj['features'] = phenotype_features(case_obj)

    # collect OMIM disorders (if available) for this case
    patient_obj['disorders'] = omim_disorders(case_obj)

    # get all snv variants for this specific individual:
    patients_variants = list(adapter.case_individual_snv_variants(case_id, patient))
    patient_obj['genomicFeatures'] = genomic_features(adapter, scout_variants=patients_variants, sample_name=patient, build=case_obj.get('genome_build'), genes_only=genes_only)

    # submit query to MME server
    patient_obj = { 'patient' : patient_obj}
    LOG.info('SUBMITTING:{}'.format(patient_obj))
    server_response = send_request(mme_url, patient_obj, token, external)

    if server_response.get('_disclaimer'):
        LOG.info('Matchmaker server was successfully contacted')
        matches = server_response.get('results')

        for n, match in enumerate(matches):
            LOG.info('result {} ----------> {}'.format(n, match))
            

@click.group()
@click.pass_context
def query(context):
    """
    View objects from the database.
    """
    pass

query.add_command(hgnc)
query.add_command(matchmaker)
