color_list = ['[255,0,0]', '[0,0,255]', '[0,255,0]', '[255,0,255]', '[0,255,255]',
              '[139, 105, 20]', '[255,97,0]', '[255, 165, 0]', '[255, 165, 0]', '[0, 191, 255]', "None"]

pen_list = [
    "",
    "width=1,",
    "width=1,style=Qt.DashLine,",
]

style_list = [
    "",
    " ,symbolBrush=(255,0,0), symbolPen='w', symbolSize=3, symbol='o'"
]

tab_list = ["motion_constrain_signal",
            "reproduction_compare_signal", "control_error"]  # tab name list

control_error = {
    " heading_error_1_0 ": [['control_command.time_meas', 'control_command.simple_debug.heading_error', '[0,0,255]', '', '', '']],
    " l_error_0_0 ": [
        ['control_command.time_meas',
            'control_command.simple_debug.lateral_error', '[255,0,0]', '', '', ''],
        ['control_command.time_meas', 'control_command.simple_debug.lateral_error', '[0,0,255]',
            '',style_list[1], 'lateral_error'],
        ['control_command.time_meas', 'control_command.simple_debug.jerk_error', '[0,255,0]', '',style_list[1], 'lateral_error']]
}

motion_constrain_signal = {  # tab signal define ,var name same with tab name
    # signal_define: x_axis_signal,y_axis_signal,color,pen,style,signal_name
    " sl_bound_0_0 ": [
        ['debug_info.behavior_result.ego_trajectory.path_points[i].s',
            'debug_info.behavior_result.ego_trajectory.path_points[i].l', '[0,0,255]', '', '', 'behavior'],
        ['debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].hard_bound.x_post',
         'debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].hard_bound.lb_post',   '[255,0,0]', '', '', 'hard_bound'],
        ['debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].hard_bound.x_post',
         'debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].hard_bound.ub_post',  '[255,0,0]', '', '', 'hard_bound'],
        ['debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].nudge_bound.x_post',
         'debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].nudge_bound.ub_post', '[255,0,255]', '',style_list[1], 'nudge_bound'],
        ['debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].nudge_bound.x_post',
         'debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].nudge_bound.lb_post', '[255,0,255]', '',style_list[1], 'nudge_bound'],
        ['debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].cross_bound.x_post',
         'debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].cross_bound.ub_post', '[255,97,0]', '',style_list[1], 'cross_bound'],
        ['debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].cross_bound.x_post',
         'debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i].cross_bound.lb_post', '[255,97,0]', '',style_list[1], 'cross_bound'], ],
    " st_bound_0_1 ": [['debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].hard_bound.x_post',
                        'debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].hard_bound.lb_post', '[255,0,0]', '', '', 'hard_ub'],
                       ['debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].hard_bound.x_post',
                        'debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].hard_bound.ub',  '[255,0,0]', '', '', 'hard_ub'],
                       ['debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].yield.x_post',
                        'debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].yield.ub_post', '[139, 105, 20]', '', '', 'yield_bound'],
                       ['debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].align_not_yield.x_post',
                        'debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].align_not_yield.lb_post', '[255,97,0]', '', '', 'align_not_yield_bnd'],
                       ['debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].align_yield.x_post',
                        'debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i].align_yield.ub_post', '[0, 191, 255]', '', '', 'align_yield_bnd'],
                       ['debug_info.behavior_result.ego_trajectory.path_points[i].t', 'debug_info.behavior_result.ego_trajectory.path_points[i].s', '[0,0,255]', '', '', 'behavior'], ],
    "theta_s_1_0": [
        ["path.path_points[i].s", "path.path_points[i].theta",
            color_list[0], pen_list[0], style_list[0], "path"],
        ["debug_info.behavior_result.ego_trajectory.path_points[i].s",
            "debug_info.behavior_result.ego_trajectory.path_points[i].theta", color_list[1], pen_list[0], style_list[0], "behavior"],
        ["debug_info.motion_debug.path_data_debug.path_points[i].s",
            "debug_info.motion_debug.path_data_debug.path_points[i].theta", color_list[2], pen_list[0], style_list[0], "motion"],
    ],
    " v_t_1_1 ": [['debug_info.behavior_result.ego_trajectory.path_points[i].t', 'debug_info.behavior_result.ego_trajectory.path_points[i].speed', '[0,0,255]', '', '', 'behavior'],
                  ['debug_info.motion_debug.speed_data_debug.speed_points[i].t',
                   'debug_info.motion_debug.speed_data_debug.speed_points[i].v', '[0,255,0]', '', '', 'motion'],
                  ['path.path_points[i].t', 'path.path_points[i].speed','[255,0,0]', '', '', 'path'],
                  ['debug_info.motion_debug.speed_constraint_debug.kappa_speed_limits[i].t',
                   'debug_info.motion_debug.speed_constraint_debug.kappa_speed_limits[i].v', '[255,0,255]', '', '', 'kappa_speed'],
                  ['debug_info.motion_debug.speed_constraint_debug.origin_map_speed_limits[i].t',
                   'debug_info.motion_debug.speed_constraint_debug.origin_map_speed_limits[i].v', '[0,255,255]', '', '', 'origin_map'],
                  ['debug_info.motion_debug.speed_constraint_debug.map_speed_limits[i].t', 'debug_info.motion_debug.speed_constraint_debug.map_speed_limits[i].v', '[139, 105, 20]', '', '', 'map'], ],
    "kappa_s_2_0": [
        ["path.path_points[i].s", "path.path_points[i].ddl",
            color_list[0], pen_list[0], style_list[0], "path.ddl"],
        ["path.path_points[i].s", "path.path_points[i].dkappa",
            color_list[1], pen_list[0], style_list[0], "path.dkappa"],
        ["debug_info.motion_debug.path_data_debug.path_points[i].s",
            "debug_info.motion_debug.path_data_debug.path_points[i].k", color_list[2], pen_list[0], style_list[0], "kappa"],
    ],
    "a_t_2_1": [
        ["path.path_points[i].t", "path.jerk[i]_post",
            color_list[0], pen_list[0], style_list[0], "path.jerk"],
        ["path.path_points[i].t", "path.path_points[i].acceleration",
            color_list[1], pen_list[0], style_list[0], "path.acc"],
        ["debug_info.behavior_result.ego_trajectory.path_points[i].t",
            "debug_info.behavior_result.ego_trajectory.path_points[i].acceleration", color_list[2], pen_list[0], style_list[0], "debug.acc"],
        ["path.path_points[i].t", "path.acc_lat[i]_post", color_list[3],
            pen_list[0], style_list[0], "path.lat_acc"],
        ["path.path_points[i].t", "path.jerk_lat[i]_post",
         color_list[4], pen_list[0], style_list[0], "path.lat_jerk"],
    ],
}

reproduction_compare_signal = {
    "sl_bound_0_0": [
        ["debug_info.motion_debug.path_data_debug.path_points[i].s",
            "debug_info.motion_debug.path_data_debug.path_points[i].l", color_list[0], pen_list[0], style_list[0], ""],
        ["debug_info_old.motion_debug.path_data_debug.path_points[i].s",
            "debug_info_old.motion_debug.path_data_debug.path_points[i].l", color_list[0], pen_list[0], style_list[1], ""],
    ],
    "st_bound_0_1": [
        ["debug_info.motion_debug.speed_data_debug.speed_points[i].t",
            "debug_info.motion_debug.speed_data_debug.speed_points[i].s", color_list[0], pen_list[0], style_list[0], ""],
        ["debug_info_old.motion_debug.speed_data_debug.speed_points[i].t",
            "debug_info_old.motion_debug.speed_data_debug.speed_points[i].s", color_list[0], pen_list[0], style_list[1], ""],
    ],
    "theta_s_1_0": [
        ["path.path_points[i].s", "path.path_points[i].theta",
            color_list[0], pen_list[0], style_list[0], ""],
        ["debug_info.motion_debug.path_data_debug.path_points[i].s",
            "debug_info.motion_debug.path_data_debug.path_points[i].theta", color_list[2], pen_list[0], style_list[0], ""],
        ["path_old.path_points[i].s",
            "path_old.path_points[i].theta", color_list[0], pen_list[0], style_list[1], ""],
        ["debug_info_old.motion_debug.path_data_debug.path_points[i].s",
            "debug_info_old.motion_debug.path_data_debug.path_points[i].theta", color_list[2], pen_list[0], style_list[1], ""],
    ],
    "v_t_1_1": [
        ["path.path_points[i].t", "path.path_points[i].speed",
            color_list[0], pen_list[0], style_list[0], ""],
        ["debug_info.motion_debug.speed_data_debug.speed_points[i].t",
            "debug_info.motion_debug.speed_data_debug.speed_points[i].v", color_list[2], pen_list[0], style_list[0], ""],
        ["path_old.path_points[i].t",
            "path_old.path_points[i].speed", color_list[0], pen_list[0], style_list[1], ""],
        ["debug_info_old.motion_debug.speed_data_debug.speed_points[i].t",
            "debug_info_old.motion_debug.speed_data_debug.speed_points[i].v", color_list[2], pen_list[0], style_list[1], ""],
    ],
    "kappa_s_2_0": [
        ["path.path_points[i].s", "path.path_points[i].ddl",
            color_list[0], pen_list[0], style_list[0], ""],
        ["path.path_points[i].s", "path.path_points[i].dkappa",
            color_list[1], pen_list[0], style_list[0], ""],
        ["debug_info.motion_debug.path_data_debug.path_points[i].s",
            "debug_info.motion_debug.path_data_debug.path_points[i].k", color_list[2], pen_list[0], style_list[0], ""],
        ["path_old.path_points[i].s", "path_old.path_points[i].ddl",
            color_list[0], pen_list[0], style_list[1], ""],
        ["path_old.path_points[i].s",
            "path_old.path_points[i].dkappa", color_list[1], pen_list[0], style_list[1], ""],
        ["debug_info_old.motion_debug.path_data_debug.path_points[i].s",
            "debug_info_old.motion_debug.path_data_debug.path_points[i].k", color_list[2], pen_list[0], style_list[1], ""],
    ],
    "a_t_2_1": [
        ["path.path_points[i].t", "path.jerk[i]",
            color_list[0], pen_list[0], style_list[0], ""],
        ["path.path_points[i].t", "path.path_points[i].acceleration",
            color_list[1], pen_list[0], style_list[0], ""],
        ["path.path_points[i].t", "path.acc_lat[i]",
         color_list[1], pen_list[0], style_list[0], ""],
        ["path.path_points[i].t", "path.jerk_lat[i]",
         color_list[1], pen_list[0], style_list[0], ""],

        ["path_old.path_points[i].t", "path_old.jerk[i]",
            color_list[0], pen_list[0], style_list[1], ""],
        ["path_old.path_points[i].t",
            "path_old.path_points[i].acceleration", color_list[1], pen_list[0], style_list[1], ""],
        ["path_old.path_points[i].t", "path_old.acc_lat[i]",
            color_list[1], pen_list[0], style_list[1], ""],
        ["path_old.path_points[i].t", "path_old.jerk_lat[i]",
            color_list[1], pen_list[0], style_list[1], ""],
    ],
}
