from indra.databases import mesh_client


def test_mesh_id_lookup_from_web():
    mesh_id = 'D003094'
    mesh_name = mesh_client.get_mesh_name_from_web(mesh_id)
    assert mesh_name == 'Collagen', mesh_name


def test_invalid_id():
    mesh_name = mesh_client.get_mesh_name_from_web('34jkgfh')
    assert mesh_name is None


def test_mesh_id_lookup_local():
    mesh_id = 'D005963'
    mesh_name = mesh_client.get_mesh_name(mesh_id, offline=True)
    assert mesh_name == 'Glucosylceramides'


def test_mesh_supplementary_id_lookup_local():
    mesh_id = 'C056331'
    mesh_name = mesh_client.get_mesh_name(mesh_id, offline=True)
    assert mesh_name == 'carbazomycin G'


def test_mesh_id_local_missing():
    mesh_id = 'XXXX'  # dummy name to make sure we don't have it offline
    mesh_name = mesh_client.get_mesh_name(mesh_id, offline=True)
    assert mesh_name is None


def test_mesh_id_fallback_to_rest():
    mesh_id = 'D015242'
    mesh_name = mesh_client.get_mesh_name(mesh_id, offline=False)
    assert mesh_name == 'Ofloxacin'


def test_mesh_term_lookup_local():
    mesh_term = 'Glucosylceramides'
    (mesh_id, mesh_name) = mesh_client.get_mesh_id_name(mesh_term, offline=True)
    assert mesh_id == 'D005963'
    assert mesh_name == mesh_term


def test_mesh_term_local_missing():
    mesh_term = 'XXXX'  # dummy term to make sure we don't have it offline
    mesh_id, mesh_name = mesh_client.get_mesh_id_name(mesh_term, offline=True)
    assert mesh_id is None
    assert mesh_name is None


def test_mesh_term_name_norm():
    # For this one, the corresponding descriptor is D016922, which is in the
    # INDRA resource file; however, the descriptor name is "Cellular
    # Senescence".  This test verifies the expected behavior that in
    # offline-only mode, "Cellular Senescence" will return the correct
    # descriptor ID, but "Cell Aging" will not, unless using the REST service.
    query_name = 'Cellular Senescence'
    mesh_id, mesh_name = mesh_client.get_mesh_id_name(query_name, offline=True)
    assert mesh_id == 'D016922'
    assert mesh_name == query_name
    query_name = 'Cell Aging'
    mesh_id, mesh_name = mesh_client.get_mesh_id_name(query_name, offline=True)
    assert mesh_id is None
    assert mesh_name is None
    mesh_id, mesh_name = mesh_client.get_mesh_id_name(query_name, offline=False)
    assert mesh_id == 'D016922'
    assert mesh_name == 'Cellular Senescence'


def test_mesh_term_lookups():
    queries = {'Breast Cancer': ('D001943', 'Breast Neoplasms'),
               'Neoplasms': ('D009369', 'Neoplasms'),
               'Intestinal Neoplasms': ('D007414', 'Intestinal Neoplasms'),
               'Carcinoma, Non-Small-Cell Lung':
                                ('D002289', 'Carcinoma, Non-Small-Cell Lung'),
               'Prostate Cancer': ('D011471', 'Prostatic Neoplasms')}
    for query_term, (correct_id, correct_name) in queries.items():
        mesh_id, mesh_name = mesh_client.get_mesh_id_name(query_term)
        assert mesh_id == correct_id, (query_term, mesh_id, correct_id)
        assert mesh_name == correct_name, (query_term, mesh_name, correct_name)


def test_mesh_isa():
    assert mesh_client.mesh_isa('D011506', 'D000602')
    assert not mesh_client.mesh_isa('D000602', 'D011506')


def test_mesh_go_mappings():
    assert mesh_client.get_go_id('D059765') == 'GO:0035825'
    assert mesh_client.get_mesh_id_from_go_id('GO:0042627') == 'D002914'
