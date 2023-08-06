'''The following functions assist in parsing old Frank Lab data using the
Frank Lab NWB extensions (franklab.extensions.yaml) for representing
aspects of the data that are not easily stored in vanilla NWB (e.g. Behavioral
apparatus/track geometries).
'''


import filterframework_to_nwb.nspike_helpers as ns
from franklab_nwb_extensions.fl_extension import (Apparatus, Edge, PointNode,
                                                  PolygonNode, SegmentNode)


def get_apparatus_from_linpos(linpos_this_epoch, name='some apparatus',
                              conversion=1.0):
    '''Make an Apparatus object representing a linearized apparatus.

    Parameters
    ----------
    linpos_this_epoch : dict
    name : str, optional
        Name of apparatus
    conversion : float
        Conversion factor to multiply linpos coordinates (i.e. for converting
        pixels to meters)

    Returns
    --------
    appar : Apparatus

    '''
    # Dummy Apparatus for epochs without one
    if not linpos_this_epoch:
        # apparatus NA for this epoch
        return Apparatus(name='NA', nodes=[], edges=[])

    nodes = []

    # Segment nodes
    seg_coords = linpos_this_epoch['segmentInfo']['segmentCoords']
    for i in range(seg_coords.shape[0]):
        # convert coords to meters using m/pixel conversion factor
        start = [conversion * c for c in list(seg_coords[i, 0:2])]
        end = [conversion * c for c in list(seg_coords[i, 2:])]
        seg_node = SegmentNode(name='segment' + str(i), coords=[start, end])
        nodes.append(seg_node)

    # Well nodes
    well_coords = linpos_this_epoch['wellSegmentInfo']['wellCoord']
    for i in range(well_coords.shape[0]):
        coords_m = [conversion * c for c in list(well_coords[i])]  # m/pixel
        well_node = PointNode(name='well' + str(i), coords=[coords_m])
        nodes.append(well_node)

    # Edges
    edges = find_edges(nodes)

    # Graph
    appar = Apparatus(name=name, nodes=nodes, edges=edges)
    return appar


def get_franklab_apparatus(epoch_metadata, behav_mod):
    '''Get the Frank Lab Apparatus object for a particular epoch.

    Note that all of the Apparatus objects must already be created and added to
    the ProcessingModule `behav_mod` that is passed into this function. This
    function is useful when iteratively processing each epoch of data and\
    mapping it onto one of a subset of pre-defined apparatuses.

    Parameters
    ----------
    epoch_metadata: dict
        The metadata dictionary from a particular epoch of the
        Filter Framework 'task' data.
    behav_mod : pynwb.ProcessingModule
        Contains all of the Frank Lab Apparatus objects. This is where we will
        look to find the appropriate apparatus for this epoch.

    Returns
    ------
    appar : Apparatus
        Frank Lab Apparatus (franklab.extensions.yaml) for this epoch

    '''
    # Extract 'type' and 'environment' from the parsed Matlab data
    if 'type' in epoch_metadata.keys():
        epoch_type = epoch_metadata['type'][0]
    else:
        epoch_type = 'NA'
    if 'environment' in epoch_metadata.keys():
        epoch_env = epoch_metadata['environment'][0]
    else:
        epoch_env = 'NA'
    # Get the Frank Lab Apparatus for this epoch
    if epoch_type == 'sleep':
        return behav_mod.data_interfaces['Sleep Box']
    elif epoch_type == 'run':
        return behav_mod.data_interfaces[epoch_env]
    else:
        raise RuntimeError("Epoch 'type' {} not supported.".format(epoch_type))


def get_franklab_task(epoch_metadata, task_mod):
    '''Get the Frank Lab Task object for a particular epoch.

    Note that all of the Task objects must already be created and added to the
    ProcessingModule `behav_mod` that is passed into this function.
    This function is useful when iteratively processing each epoch of data and
    mapping it onto one of a subset of pre-defined Tasks.

    Parameters
    ----------
    epoch_metadata: dict
        The metadata dictionary from a particular epoch of the
        Filter Framework 'task' data.
    behav_mod : pynwb.ProcessingModule
        Contains all of the Frank Lab Apparatus objects. This is where we will
        look to find the appropriate apparatus for this epoch.

    Returns
    -------
    task : Task
        Frank Lab Task (franklab.extensions.yaml) for this epoch

    '''
    # Extract epoch 'type' from the parsed Matlab data
    if 'type' in epoch_metadata.keys():
        epoch_type = epoch_metadata['type'][0]
    else:
        epoch_type = 'NA'
    # Return the appropriate Frank Lab Taks
    if epoch_type == 'sleep':
        return task_mod.data_interfaces["Sleep"]
    elif epoch_type == 'run':
        return task_mod.data_interfaces["W-Alternation"]
    else:
        raise RuntimeError("Epoch 'type' {} not supported.".format(epoch_type))


def get_franklab_nodes(points, segments, polygons):
    '''Create a list of Frank Lab PointNode, SegmentNode, and PolygonNode
    objects, given a set of Python dictionaries where each entry represents the
    geometrical coordinates of a single point, segment, or polygon that we want
    to make a Node for.

    Parameters
    ----------
    points :  dict
        Each key is the name of a point, and each value is a 1x2 list with the
        xy coordinates of the point.
    segments :  dict
        Each key is the name of a segement, and each value is a 2x2 list
        with the xy coordinates of the start and end point of the segment
    polygons : dict
        Each key is the name of a polygon, and each value is a nx2 list
        with the xy coordinates of the vertices in the polygon

    Returns
    -------
    nodes : list
        Frank Lab PointNode, SegmentNode, and PolygonNode objects

    '''
    nodes = []
    for name, point in points.items():
        # wrap [x,y] point in a list so all apparatus coords (point, segment,
        # or polygon) are nested lists
        nodes.append(PointNode(name=name, coords=[point]))
    for name, segment in segments.items():
        nodes.append(SegmentNode(name=name, coords=segment))
    for name, polygon in polygons.items():
        nodes.append(PolygonNode(
            name=name, coords=polygon, interior_coords=None))
    return nodes


def separate_epochs_by_apparatus(data_dir, animal, day):
    '''For data from the CRCNS hc-6 dataset. Returns which epochs in a given\
    day that the animal was in the Sleep Box, W-track A, or W-track B.

    Parameters
    ---------
    data_dir : str
    animal: str
    day: int

    Returns
    -------
    sleep_epochs : list
        Epochs where the animal was in the sleep box
    wtrackA_epochs : list
        Epochs where the animal was on W-track A
    wtrackB_epochs : list
        Epochs where the animal was on W-track B

    '''

    sleep_epochs, wtrackA_epochs, wtrackB_epochs = [], [], []
    all_epochs_metadata = ns.parse_franklab_task_data(data_dir, animal, day)
    for epoch_num, epoch_metadata in all_epochs_metadata.items():
        if 'environment' in epoch_metadata.keys():
            if epoch_metadata['environment'][0] == 'TrackA':
                wtrackA_epochs.append(epoch_num)
            else:
                wtrackB_epochs.append(epoch_num)
        else:
            sleep_epochs.append(epoch_num)
    return sleep_epochs, wtrackA_epochs, wtrackB_epochs


def coords_intersect(n1, n2, tol=0.01):
    '''Returns True if the input points are equivalent.

    Parameters
    ----------
    n1 : list of lists, shape (1, 2)
    n2 : list of lists, shape (1, 2)
    tol : float
        Tolerance within which to consider floating-point values equal

    Returns
    -------
    is_intersect : bool
        True if n1 == n2 within some tolerance.

    '''
    for c1 in n1.coords:
        for c2 in n2.coords:
            if (abs(c1[0] - c2[0]) <= tol and abs(c1[1] - c2[1]) <= tol):
                return True
    return False


def find_edges(node_list):
    '''Find pairs of Frank Lab nodes that share at least one xy coordinate.

    Parameters
    ----------
    node_list : list of lists, shape (1, n)
        List of objects inheriting from Frank Lab Node

    Returns
    -------
    ret_edges : list of lists, shape (1, m)
        List of Frank Lab Edge objects, each of which contains the
        names of two Nodes that share at least one coordinate
    '''
    edges = []
    for n1 in node_list:
        for n2 in node_list:
            if ((n1.name == n2.name) or
                ([n1.name, n2.name] in edges) or
                    ([n2.name, n1.name] in edges)):
                continue
            elif coords_intersect(n1, n2):
                edges.append([n1.name, n2.name])
    ret_edges = []
    for (n1, n2) in edges:
        ret_edges.append(Edge(name=n1 + '<->' + n2, edge_nodes=[n1, n2]))
    return ret_edges
