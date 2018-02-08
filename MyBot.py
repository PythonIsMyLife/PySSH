"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging
import math

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("OldMonkBot")
# Then we print our start message to the logs
logging.info("Starting my MonkBot!")

turn = 0


def new_navigate(ship, target, game_map, max_corrections=90, angular_step=1, spin=False):
    """
    Move a ship to a specific target position (Entity). It is recommended to place the position
    itship here, else navigate will crash into the target. If avoid_obstacles is set to True (default)
    will avoid obstacles on the way, with up to max_corrections corrections. Note that each correction accounts
    for angular_step degrees difference, meaning that the algorithm will naively try max_correction degrees before giving
    up (and returning None). The navigation will only consist of up to one command; call this method again
    in the next turn to continue navigating to the position.

    :param Entity target: The entity to which you will navigate
    :param game_map.Map game_map: The map of the game, from which obstacles will be extracted
    :param int speed: The (max) speed to navigate. If the obstacle is nearer, will adjust accordingly.
    :param bool avoid_obstacles: Whether to avoid the obstacles in the way (simple pathfinding).
    :param int max_corrections: The maximum number of degrees to deviate per turn while trying to pathfind. If exceeded returns None.
    :param int angular_step: The degree difference to deviate if the original destination has obstacles
    :param bool ignore_ships: Whether to ignore ships in calculations (this will make your movement faster, but more precarious)
    :param bool ignore_planets: Whether to ignore planets in calculations (useful if you want to crash onto planets)
    :return string: The command trying to be passed to the Halite engine or None if movement is not possible within max_corrections degrees.
    :rtype: str
    """
    # Assumes a position, not planet (as it would go to the center of the planet otherwise)
    if max_corrections <= 0:
        return None
    distance = min(hlt.constants.MAX_SPEED*2, ship.calculate_distance_between(target))
    speed = min(distance, hlt.constants.MAX_SPEED)
    angle = ship.calculate_angle_between(target)
    target_dx = math.cos(math.radians(angle)) * distance + ship.x
    target_dy = math.sin(math.radians(angle)) * distance + ship.y

    for obstacle in possibleObstacles[ship]:
        if hlt.collision.intersect_segment_circle(ship, hlt.entity.Position(x=target_dx, y=target_dy), obstacle[0], fudge=0.6):
            if spin:
                new_target_dx = math.cos(math.radians(angle - angular_step)) * distance
                new_target_dy = math.sin(math.radians(angle - angular_step)) * distance
                new_target = hlt.entity.Position(ship.x + new_target_dx, ship.y + new_target_dy)
                nav = new_navigate(ship, new_target, game_map, int(max_corrections / 2) - 1, -angular_step)

                new_target_dx = math.cos(math.radians(angle + angular_step)) * distance
                new_target_dy = math.sin(math.radians(angle + angular_step)) * distance
                new_target = hlt.entity.Position(ship.x + new_target_dx, ship.y + new_target_dy)
                nav2 = new_navigate(ship, new_target, game_map, int(max_corrections / 2) - 1, angular_step)
                if nav:
                    if nav2:
                        if nav > nav2:
                            angle = angle + 360 - (int(max_corrections / 2) - nav) * angular_step
                        else:
                            angle = angle + (int(max_corrections / 2) - nav2) * angular_step
                    else:
                        angle = angle + 360 - (int(max_corrections / 2) - nav) * angular_step
                elif nav2:
                    angle = angle + (int(max_corrections / 2) - nav2) * angular_step
                else:
                    return None
            else:
                new_target_dx = math.cos(math.radians(angle + 360 + angular_step)) * distance
                new_target_dy = math.sin(math.radians(angle + 360 + angular_step)) * distance
                new_target = hlt.entity.Position(ship.x + new_target_dx, ship.y + new_target_dy)
                return new_navigate(ship, new_target, game_map, max_corrections - 1, angular_step)

    if not spin:
        return max_corrections
            # else:
            #     speed = ship.calculate_distance_between(obstacle[0]) - abs(checkDist)
            #     target_dx = math.cos(math.radians(angle)) * speed + ship.x
            #     target_dy = math.sin(math.radians(angle)) * speed + ship.y

    target_dx = math.cos(math.radians(angle)) * distance + ship.x
    target_dy = math.sin(math.radians(angle)) * distance + ship.y
    fakeShip = hlt.entity.Position(x=target_dx, y=target_dy)
    fakeShip.radius = ship.radius
    for ship3 in ships:
            dist = ship3.calculate_distance_between(fakeShip)
            if dist <= ship3.radius + hlt.constants.MAX_SPEED + fakeShip.radius + 0.1:
                possibleObstacles[ship3].append((fakeShip, dist))

    # cos = math.cos(math.radians(angle + angular_step))
    # sin = math.sin(math.radians(angle + angular_step))
    #
    # x = []
    # y = []
    # blocked = False
    #
    # for j in range(1, round(distance) * 2 + 1):
    #     x.append(round(ship.x + cos * j * 0.5))
    #     y.append(round(ship.y + sin * j * 0.5))
    #     if (x[-1], y[-1]) in positionGrid:
    #         if positionGrid[(x[-1], y[-1])] != ship.id:
    #             blocked = True
    #             break
    #
    # if not blocked:
    #     for j in range(0, round(distance) * 2):
    #         add_to_pos_grid(ship.radius, x[j], y[j], ship.id)
    # else:
    #     new_target_dx = math.cos(math.radians(angle + angular_step)) * distance
    #     new_target_dy = math.sin(math.radians(angle + angular_step)) * distance
    #     new_target = hlt.entity.Position(ship.x + new_target_dx, ship.y + new_target_dy)
    #     return new_navigate(ship, new_target, game_map, speed, True, max_corrections - 1, angular_step)
    return ship.thrust(speed, angle)


def get_attackers(myShips, theirShips):

    attackers = []
    for enemyShip in theirShips:
        # Attackers aren't docking
        if enemyShip.docking_status != enemyShip.DockingStatus.UNDOCKED:
            continue

        bestDist = game_map.width + game_map.height
        attackerFound = False
        for planet in game_map.all_planets():
            # I only want attackers for my planets

            tempDist = enemyShip.calculate_distance_between(planet)
            if tempDist < bestDist:
                attackerFound = True
                triple = tempDist, enemyShip, planet
                bestDist = tempDist

        if attackerFound and bestDist < triple[2].radius * triple[2].radius:
            if triple[2].owner != game_map.get_me():
                continue
            attackers.append(triple)

    attackers = sorted(attackers, key=lambda tup: tup[0])

    for attacker in attackers:
        bestDist = attacker[2].radius * attacker[2].radius
        defenderFound = False
        bestDefender = None

        for defender in myShips:
            tempDist = defender.calculate_distance_between(attacker[1])
            if tempDist < bestDist:
                defenderFound = True
                bestDefender = defender
                bestDist = tempDist

        if defenderFound:
            navigate_command = new_navigate(bestDefender,
                                            bestDefender.closest_point_to(attacker[1]),
                                            game_map,
                                            max_corrections=correctionsAllowed,
                                            angular_step=stepsAllowed,
                                            spin=True)
            if navigate_command:
                command_queue.append(navigate_command)
                myShips.remove(bestDefender)

    return myShips


# def add_to_pos_grid(radius, x, y, id):
#     radius = 1
#     for ix in range(round(x - radius), round(x + radius) + 1):
#         for iy in range(round(y - radius), round(y + radius) + 1):
#             if (ix, iy) in positionGrid:
#                 positionGrid[(ix, iy)] = -1
#             else:
#                 positionGrid[(ix, iy)] = id
#             logging.info(str((ix, iy)))

try:
    while True:
        turn = turn + 1
        # TURN START
        # Update the map for the new turn and get the latest version
        game_map = game.update_map()
        logging.info("Turn: " + str(turn))

        # Here we define the set of commands to be sent to the Halite engine at the end of the turn
        command_queue = []

        # The list of potential attackers to be used by the attacker finder function
        attackers = []

        # The list of docked enemy ships
        dockedEnemies = []

        # The list of docked friendly ships
        dockedFriendlies = []

        # The grid used for ensuring that no 2 ships move at the same position
        positionGrid = {}

        # Sorting function to put enemy ships into their corresponding lists
        for player in game_map.all_players():
            if player == game_map.get_me():
                continue

            for ship2 in player.all_ships():
                if ship2.docking_status == ship2.DockingStatus.UNDOCKED:
                    attackers.append(ship2)
                else:
                    dockedEnemies.append(ship2)
                    # add_to_pos_grid(ship2.radius, ship2.x, ship2.y, ship2.id)

        #
        colonizePlanets = []
        conquerPlanets = []

        for planet in game_map.all_planets():
            # Search for planets without owner or planets from me that aren't full
            if planet.owner is None or (planet.owner is game_map.get_me() and not planet.is_full()):
                for i in range(planet.num_docking_spots - len(planet.all_docked_ships())):
                    colonizePlanets.append(planet)
            # Also, search for enemy planets
            elif planet.owner is not game_map.get_me():
                conquerPlanets.append(planet)

        shipsOld = game_map.get_me().all_ships()
        ships = []
        for ship in shipsOld:
            # add_to_pos_grid(ship.radius, ship.x, ship.y, ship.id)
            if ship.docking_status == ship.DockingStatus.UNDOCKED:
                ships.append(ship)
            else:
                dockedFriendlies.append(ship)

        possibleObstacles = {}
        tests = game_map.all_planets()
        #tests.extend(dockedEnemies)
        tests.extend(dockedFriendlies)
        tests.extend(ships)

        for ship in ships:
            possibleObstacles[ship] = []
            for obstacle in tests:
                if obstacle == ship:
                    continue
                dist = ship.calculate_distance_between(obstacle)
                if dist <= ship.radius + hlt.constants.MAX_SPEED + obstacle.radius + 0.1:
                    possibleObstacles[ship].append((obstacle, dist))

        if len(shipsOld) > 160:
            correctionsAllowed = 22
            stepsAllowed = 8
        else:
            correctionsAllowed = 44
            stepsAllowed = 4

        # Find attackers near our planets and defend
        ships = get_attackers(ships, attackers)

        couples = []
        for ship in ships:
            for planet in colonizePlanets:
                # if ship
                triple = ship.calculate_distance_between(planet), ship, planet
                couples.append(triple)

            couples = sorted(couples, key=lambda tup: tup[0])

        # Fly to colonizable or non-full own planets first
        while len(colonizePlanets) and len(ships) > 0:

            if len(couples) > 0:
                triple = couples.pop(0)
            else:
                break
            while len(couples) > 0 and (ships.count(triple[1]) == 0 or colonizePlanets.count(triple[2]) == 0):
                triple = couples.pop(0)

            bestShip = triple[1]
            bestPlanet = triple[2]
            if bestShip.can_dock(bestPlanet):
                # We add the command by appending it to the command_queue
                command_queue.append(bestShip.dock(bestPlanet))
            else:
                navigate_command = new_navigate(bestShip,
                                                bestShip.closest_point_to(bestPlanet),
                                                game_map,
                                                max_corrections=correctionsAllowed,
                                                angular_step=stepsAllowed,
                                                spin=True)
                if navigate_command:
                    command_queue.append(navigate_command)

            ships.remove(bestShip)
            colonizePlanets.remove(bestPlanet)

        # For every ship that I control that is not defending or colonizing
        for ship in ships:
            navigate_command = None

            bestDist = game_map.width + game_map.height
            bestPlanet = None
            bestEnemyPlanet = None
            bestEnemyDist = bestDist
            bestShipDist = bestDist
            planetFound = False
            enemyPlanetFound = False
            shipFound = False
            i = 0

            # Search for docked enemy ships
            bestShipDist = game_map.width + game_map.height
            bestShip = None
            bestShip = None
            for ship2 in dockedEnemies:
                tempDist = ship.calculate_distance_between(ship2)
                if tempDist < bestShipDist:
                    bestShipDist = tempDist
                    bestShip = ship2
                    shipFound = True

            # Otherwise, search for nearby enemy planets
            if not shipFound:
                for planet in conquerPlanets:
                    tempDist = ship.calculate_distance_between(planet)
                    if tempDist < bestEnemyDist:
                        bestEnemyDist = tempDist
                        bestEnemyPlanet = planet
                        enemyPlanetFound = True

            # If a docked ship was found, attack
            if not navigate_command and shipFound:
                navigate_command = new_navigate(ship,
                                                ship.closest_point_to(bestShip),
                                                game_map,
                                                max_corrections=correctionsAllowed,
                                                angular_step=stepsAllowed,
                                                spin=True)

            # Otherwise, fly towards an enemy planet
            if not navigate_command and enemyPlanetFound:
                if len(game_map.obstacles_between(ship, bestEnemyPlanet, hlt.entity.Planet)) == 1:
                    navigate_command = ship.navigate(
                        bestEnemyPlanet,
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False,
                        ignore_planets=True,
                        max_corrections=correctionsAllowed,
                        angular_step=stepsAllowed)
                else:
                    navigate_command = new_navigate(ship,
                                                    bestEnemyPlanet,
                                                    game_map,
                                                    max_corrections=correctionsAllowed,
                                                    angular_step=stepsAllowed,
                                                    spin=True)

            if navigate_command:
                command_queue.append(navigate_command)
        # Send our set of commands to the Halite engine for this turn
        game.send_command_queue(command_queue)
        #logging.info(str(possibleObstacles))
        # TURN END
except Exception as e:
    logging.exception(e)
# GAME END