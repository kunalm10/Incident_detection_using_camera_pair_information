import database
import time


cnx = database.get_connection()
cursor = cnx.cursor()
from datetime import datetime

current_datetime = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# reference_camera_id = 1
# reference_to_neighbor_direction = 'S'
# neighbor_to_reference_direction = 'W'
# reference_cam_flow_rate = 800
# neighbor_cam_flow_rate = 750

x = 0.8
y = 1.2
flow_rate_zero = 0
flow_rate_normal = 1500
flow_rate_moderate = 2500

time_to_run_every_x_seconds = 0  # the databse will update in every 5 seconds


def get_all_cameras():
    query = "SELECT camera_id FROM camera_list"
    cursor.execute(query)
    result_set = cursor.fetchall()
    result = []
    for row in result_set:
        result.append([row][0][0])
    return result


def get_neighbor_cameras(reference_camera_id):
    query = "SELECT distinct neighbor_camera_id FROM camera_neighbor WHERE reference_camera_id = {}".format(reference_camera_id)
    cursor.execute(query)
    result_set = cursor.fetchall()
    result = []
    for row in result_set:
        result.append([row][0][0])
    return result


def get_reference_and_neighbor_camera_valid_direction_pair(reference_camera_id, neighbor_camera_id):
    query = "SELECT reference_to_neighbor_direction, neighbor_to_reference_direction, direction_match_flag " \
            "FROM camera_neighbor WHERE reference_camera_id = %i AND neighbor_camera_id = %i" % (reference_camera_id, neighbor_camera_id)
    cursor.execute(query)
    result_set = cursor.fetchall()

    result = []
    if result_set != None:
        for row in result_set:
            result_dict = dict()
            result_dict['reference_to_neighbor_direction'] = row[0]
            result_dict['neighbor_to_reference_direction'] = row[1]
            result_dict['direction_match_flag'] = row[2]
            result.append(result_dict)
    return result  # this is a list of dictonaries which contain neighbor camera, reference_to_neighbor_direction,
    # and neighbor_to_reference_direction


def get_current_direction(camera_id):
    query = "SELECT current_direction FROM camera_list WHERE camera_id = %i" % (camera_id)
    cursor.execute(query)
    result_set = cursor.fetchone()
    result = None
    if result_set != None:
        result = result_set[0]
    return result


def get_flow_rate(camera_id, direction, side):
    query = "SELECT distinct(avg_traffic_flow) FROM traffic_status td, lane_details ld, cam_facing_road cfr " \
            "WHERE cfr.camera_road_id = ld.cam_road_id and ld.lane_id = td.lane_id and cfr.camera_id = {0} " \
            "and cfr.direction =  '{1}'  and ld.lane_annotation > 0".format(camera_id, direction)
    if side == 'left':
        query = "SELECT distinct(avg_traffic_flow) FROM traffic_status td, lane_details ld, cam_facing_road cfr " \
                "WHERE cfr.camera_road_id = ld.cam_road_id and ld.lane_id = td.lane_id and cfr.camera_id = {0} " \
                "and cfr.direction =  '{1}'  and ld.lane_annotation < 0".format(camera_id, direction)

    cursor.execute(query)
    result_set = cursor.fetchone()
    result = None
    if result_set != None:
        result = result_set[0]
    return result


def get_road_name_from_jam_status(reference_camera_id, neighbor_camera_id):
    query = "SELECT road_name FROM jam_status_current WHERE reference_cam_id = {} AND neighbor_cam_id = {}".format(reference_camera_id, neighbor_camera_id)
    cursor.execute(query)
    result_set = cursor.fetchone()
    result = None
    if result_set != None:
        result = result_set[0]
    return result


def update_jam_status_current(datetime, reference_camera_id, neighbor_camera_id, reference_cam_current_direction,
                              neighbor_cam_current_direction, JAM_STATUS_left_lane, JAM_STATUS_right_lane):
    query = "UPDATE jam_status_current SET reference_current_direction = %s, neighbor_current_direction = %s, right_lane_status = %s, creation_datetime = %s, " \
            "left_lane_status = %s WHERE reference_cam_id = %s AND neighbor_cam_id = %s"
    cursor.execute(query, (
        str(reference_cam_current_direction), str(neighbor_cam_current_direction), str(JAM_STATUS_right_lane),
        str(datetime),
        str(JAM_STATUS_left_lane), int(reference_camera_id), int(neighbor_camera_id)))
    cnx.commit()


def insert_jam_status_history(datetime, reference_camera_id, neighbor_camera_id, reference_cam_current_direction,
                              neighbor_cam_current_direction, JAM_STATUS_left_lane, JAM_STATUS_right_lane):
    print(datetime, reference_camera_id, neighbor_camera_id, reference_cam_current_direction,
          neighbor_cam_current_direction, JAM_STATUS_left_lane, JAM_STATUS_right_lane)
    print('-----------------------------------------------\n\n----------------------------------------------------')
    road_name = get_road_name_from_jam_status(reference_camera_id, neighbor_camera_id)
    query = "INSERT INTO jam_status_history (`reference_cam_id`, `neighbor_cam_id`, `road_name`, `reference_current_direction`, " \
            "`neighbor_current_direction`, `right_lane_status`, `left_lane_status`, `creation_datetime`) VALUES (" \
            "%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (
        str(reference_camera_id), str(neighbor_camera_id), str(road_name), str(reference_cam_current_direction),
        str(neighbor_cam_current_direction),
        str(JAM_STATUS_left_lane), str(JAM_STATUS_right_lane), str(datetime)))
    cnx.commit()


def make_pair(a, b):
    if a < b:
        return [a, b]
    else:
        return [b, a]


def flow_rate_compare(reference_camera_id, neighbor_camera_id, reference_cam_current_direction,
                      neighbor_cam_current_direction, reference_cam_flow_rate_right, reference_cam_flow_rate_left,
                      neighbor_cam_flow_rate_right, neighbor_cam_flow_rate_left, direction_match_flag):
    # Check if reference and neigbor camera have same direction
    if direction_match_flag == 'SAME':
        # direction illustration function block
        direction_illustration_same_direction(reference_camera_id, neighbor_camera_id, reference_cam_current_direction)

        print("both cameras are facing in same direction\n"
              "so we compare reference left lane with neighbor left lane and reference right lane with neighbor right lane\n")

        if neighbor_cam_flow_rate_left not in range(int(x * int(reference_cam_flow_rate_left)),
                                                    int(y * int(reference_cam_flow_rate_left))):
            JAM_STATUS_left_lane = "HIGH"
        else:
            if neighbor_cam_flow_rate_left in range(flow_rate_zero, flow_rate_normal):
                JAM_STATUS_left_lane = "NORMAL"
            elif neighbor_cam_flow_rate_left in range(flow_rate_normal, flow_rate_moderate):
                JAM_STATUS_left_lane = "MODERATE"
            else:
                JAM_STATUS_left_lane = "HIGH"
        if neighbor_cam_flow_rate_right not in range(int(x * int(reference_cam_flow_rate_right)),
                                                     int(y * int(reference_cam_flow_rate_right))):
            JAM_STATUS_right_lane = "HIGH"
        else:
            if neighbor_cam_flow_rate_right in range(flow_rate_zero, flow_rate_normal):
                JAM_STATUS_right_lane = "NORMAL"
            elif neighbor_cam_flow_rate_right in range(flow_rate_normal, flow_rate_moderate):
                JAM_STATUS_right_lane = "MODERATE"
            else:
                JAM_STATUS_right_lane = "HIGH"
    else:
        # direction illustration function block
        direction_illustration_different_direction(reference_camera_id, neighbor_camera_id,
                                                   reference_cam_current_direction, neighbor_cam_current_direction)

        print("both cameras are looking in different direction\n"
              "so we compare reference left lane with neighbor right lane and reference right lane with neighbor left lane\n")

        if neighbor_cam_flow_rate_left not in range(int(x * int(reference_cam_flow_rate_right)),
                                                    int(y * int(reference_cam_flow_rate_right))):
            JAM_STATUS_right_lane = "HIGH"
        else:
            if neighbor_cam_flow_rate_right in range(flow_rate_zero, flow_rate_normal):
                JAM_STATUS_right_lane = "NORMAL"
            elif neighbor_cam_flow_rate_right in range(flow_rate_normal, flow_rate_moderate):
                JAM_STATUS_right_lane = "MODERATE"
            else:
                JAM_STATUS_right_lane = "HIGH"
        if neighbor_cam_flow_rate_right not in range(int(x * int(reference_cam_flow_rate_left)),
                                                     int(y * int(reference_cam_flow_rate_left))):
            JAM_STATUS_left_lane = "HIGH"
        else:
            if neighbor_cam_flow_rate_left in range(flow_rate_zero, flow_rate_normal):
                JAM_STATUS_left_lane = "NORMAL"
            elif neighbor_cam_flow_rate_left in range(flow_rate_normal, flow_rate_moderate):
                JAM_STATUS_left_lane = "MODERATE"
            else:
                JAM_STATUS_left_lane = "HIGH"
    return (JAM_STATUS_right_lane, JAM_STATUS_left_lane)


# this function is just for debugging purpose, where ever this function is used, that part can be commented and the
# code will still run smooth.
def direction_illustration_same_direction(reference_camera_id, neighbor_camera_id, reference_cam_current_direction):
    if reference_cam_current_direction == 'W':
        reference_direction_illustration = '--->'
    elif reference_cam_current_direction == 'E':
        reference_direction_illustration = '<---'
    elif reference_cam_current_direction == 'N':
        reference_direction_illustration = '/ \\n' \
                                           ' | \n' \
                                           ' | \n'
    elif reference_cam_current_direction == 'S':
        reference_direction_illustration = ' | \n' \
                                           ' | \n' \
                                           '\ /'
    print("current orientation of cameras\n"
          "--------------------------------------------\n"
          "CAM %s                                CAM%s \n"
          "%s                                 %s\n"
          "---------------------------------------------\n"
          % (reference_camera_id, neighbor_camera_id, reference_direction_illustration,
             reference_direction_illustration))


# this function is just for debugging purpose, where ever this function is used, that part can be commented and the
# code will still run smooth.
def direction_illustration_different_direction(reference_camera_id, neighbor_camera_id, reference_cam_current_direction,
                                               neighbor_cam_current_direction):
    if reference_cam_current_direction == 'W' and neighbor_cam_current_direction == 'E':
        reference_direction_illustration = '--->'
        neighbor_direction_illustration = '<---'
    elif reference_cam_current_direction == 'E' and neighbor_cam_current_direction == 'W':
        reference_direction_illustration = '<---'
        neighbor_direction_illustration = '--->'
    elif reference_cam_current_direction == 'N' and neighbor_cam_current_direction == 'S':
        reference_direction_illustration = '/ \\n' \
                                           ' | \n' \
                                           ' | \n'
        neighbor_direction_illustration = ' | \n' \
                                          ' | \n' \
                                          '\ /'
    elif reference_cam_current_direction == 'S' and neighbor_cam_current_direction == 'N':
        reference_direction_illustration = ' | \n' \
                                           ' | \n' \
                                           '\ /'
        neighbor_direction_illustration = '/ \\n' \
                                          ' | \n' \
                                          ' | \n'
    print("current orientation of cameras\n"
          "--------------------------------------------\n"
          "CAM %s                                CAM %s \n"
          "%s                                  %s\n"
          "---------------------------------------------\n"
          % (
              reference_camera_id, neighbor_camera_id, reference_direction_illustration,
              neighbor_direction_illustration))


def generate_status(cam_list):
    compared_pairs = []
    start_time = time.time()
    # make a list of all the cameras available to us
    reference_cameras_list = cam_list  #
    # print(reference_cameras_list)

    for index, reference_camera_id in enumerate(reference_cameras_list):
        print("camera index = {}".format(index + 1))
        print("Reference_cam_id = {}".format(reference_camera_id))
        # Make a list of dictionaries which contain reference_to_neighbor_direction,
        # and neighbor_to_reference_direction, direction flag
        neighbor_cameras = get_neighbor_cameras(reference_camera_id)
        print('neighbor_camera = {}'.format(neighbor_cameras))
        # Taking reference camera current direction
        reference_cam_current_direction = get_current_direction(reference_camera_id)
        print('reference_camera_current_direction = {}\n'.format(reference_cam_current_direction))

        # Check if reference camera current direction is available to us, if not do not make any comparision,
        # this camera will be skipped
        if reference_cam_current_direction is not None:
            # Now, use the previously generated neighbor camera list to check all the neighbor cameras one by one.
            # This for loop should be intented towards right.

            for neighbor_camera_id in neighbor_cameras:
                print('Neighbor_camera_id = ', neighbor_camera_id)
                neighbor_cam_current_direction = get_current_direction(neighbor_camera_id)
                print('neighbor_cam_current_direction = {}'.format(neighbor_cam_current_direction))
                if neighbor_cam_current_direction is not None:
                    neighbor_camera_details = get_reference_and_neighbor_camera_valid_direction_pair(
                        reference_camera_id, neighbor_camera_id)

                    for count, each_neighbor_camera in enumerate(neighbor_camera_details):
                        neighbor_to_reference_direction = each_neighbor_camera.get("neighbor_to_reference_direction")
                        reference_to_neighbor_direction = each_neighbor_camera.get("reference_to_neighbor_direction")
                        direction_match_flag = str(each_neighbor_camera.get("direction_match_flag").upper())

                        print('CHECKING CURRENT DIRECTION WITH STORED VALID DIRECTION PAIRS\n')
                        print('Neighbor_cam_to_Reference_cam_direction, Reference_cam_to_Neighbor_cam_direction = ',
                              neighbor_to_reference_direction, reference_to_neighbor_direction)
                        print('    Neighbor_cam_Current_direction,          Reference_cam_Current_direction     = ',
                              neighbor_cam_current_direction, reference_cam_current_direction, '\n');
                        # we first check if the current directions of reference and neighbor cameras match with one of the
                        # valid direction pair stored in the database.
                        if reference_cam_current_direction == reference_to_neighbor_direction and neighbor_cam_current_direction == neighbor_to_reference_direction:
                            print(
                                '--------------------------current directions match one of the DIRECTION PAIR(S) in which flow rate comparision is POSSIBLE-------------------------- \n')
                            print(
                                '-------------------------------------------fetching flow rate from database to determine the status of JAM-------------------------------------------\n')

                            # fetch the flow rates of neighbor camera and reference camera
                            neighbor_cam_flow_rate_right = get_flow_rate(neighbor_camera_id,
                                                                         neighbor_cam_current_direction, 'right')
                            neighbor_cam_flow_rate_left = get_flow_rate(neighbor_camera_id,
                                                                        neighbor_cam_current_direction, 'left')

                            reference_cam_flow_rate_right = get_flow_rate(reference_camera_id,
                                                                          reference_cam_current_direction, 'right')
                            reference_cam_flow_rate_left = get_flow_rate(reference_camera_id,
                                                                         reference_cam_current_direction, 'left')

                            print('flow rate of reference camera right,left = ', reference_cam_flow_rate_right,
                                  reference_cam_flow_rate_left)
                            print('flow rate of neighbor camera right,left = ', neighbor_cam_flow_rate_right,
                                  neighbor_cam_flow_rate_left, '\n')

                            # Check if any of the flow_rate value is None, if that's the case then flow rate comparisions is not possible
                            if neighbor_cam_flow_rate_left != None and neighbor_cam_flow_rate_right != None and \
                                    reference_cam_flow_rate_left != None and reference_cam_flow_rate_right != None:

                                # this if statement shold be intended towards right
                                JAM_STATUS_right_lane, JAM_STATUS_left_lane = flow_rate_compare(reference_camera_id,
                                                                                                neighbor_camera_id,
                                                                                                reference_cam_current_direction,
                                                                                                neighbor_cam_current_direction,
                                                                                                reference_cam_flow_rate_right,
                                                                                                reference_cam_flow_rate_left,
                                                                                                neighbor_cam_flow_rate_right,
                                                                                                neighbor_cam_flow_rate_left,
                                                                                                direction_match_flag)
                                update_jam_status_current(current_datetime, reference_camera_id, neighbor_camera_id,
                                                          reference_cam_current_direction,
                                                          neighbor_cam_current_direction, JAM_STATUS_left_lane,
                                                          JAM_STATUS_right_lane)
                                insert_jam_status_history(current_datetime, reference_camera_id, neighbor_camera_id,
                                                          reference_cam_current_direction,
                                                          neighbor_cam_current_direction, JAM_STATUS_left_lane,
                                                          JAM_STATUS_right_lane)

                                print('JAM STATUS of left lane of ROAD which has camera', reference_camera_id,
                                      'monitoring', reference_cam_current_direction, 'direction = ',
                                      JAM_STATUS_left_lane)
                                print('JAM STATUS of right lane of ROAD which has camera', reference_camera_id,
                                      'monitoring', reference_cam_current_direction, 'direction = ',
                                      JAM_STATUS_right_lane)
                            else:
                                JAM_STATUS_right_lane, JAM_STATUS_left_lane = 'UNKNOWN', 'UNKNOWN'
                                update_jam_status_current(current_datetime, reference_camera_id, neighbor_camera_id,
                                                          reference_cam_current_direction,
                                                          neighbor_cam_current_direction, JAM_STATUS_left_lane,
                                                          JAM_STATUS_right_lane)
                                insert_jam_status_history(current_datetime, reference_camera_id, neighbor_camera_id,
                                                          reference_cam_current_direction,
                                                          neighbor_cam_current_direction, JAM_STATUS_left_lane,
                                                          JAM_STATUS_right_lane)

                                print('JAM STATUS of left lane of ROAD which has camera', reference_camera_id,
                                      'monitoring', reference_cam_current_direction, 'direction = ',
                                      JAM_STATUS_left_lane)
                                print('JAM STATUS of right lane of ROAD which has camera', reference_camera_id,
                                      'monitoring', reference_cam_current_direction, 'direction = ',
                                      JAM_STATUS_right_lane)
                            break;

                        else:
                            print(
                                '-----------current direction does not match the STORED VALID DIRECTION PAIR(S) in which we can compare flow rate----------\n'
                                '-------------------------------------------so flow rate comparision is not possible------------------------------------------ \n')
                else:
                    print(
                        "CAN'T DETERMINE STATUS of the ROAD because can't read the DIRECTION of the Neighbor Camera\n")

        else:
            print("CAN'T DETERMINE STATUS of the ROAD because can't read the DIRECTION of the Reference Camera")
        print('\n\n\n')
        print('-' * 150)
        print('Moving on to next REFERENCE CAMERA')
        print('-' * 150)
        print('\n\n\n\n')
        # time.sleep(1.5)

    stop_time = time.time()
    total_time = (stop_time - start_time)
    print("total time of execution on {} cameras = {} seconds\n\n\n\n\n\n\n".format(index + 1, total_time))
    time.sleep(time_to_run_every_x_seconds)

# generate_status(get_all_cameras())
