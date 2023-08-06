from soco import SoCo
import dateutil.parser
import time
import sys

class SonosExtras(SoCo):
    def stop_after(self, songs):
        if self.get_current_transport_info()["current_transport_state"] == "PLAYING":
            while songs >= 1:
                if songs > 1:
                    print("\rStopping afer " + songs.__str__() + " songs...", end = '         \r\n', flush=True)
                else:
                    print("\rStopping afer current song ...", end = '         \r\n', flush=True)
    
                remainingSeconds = self._curr_track_remaining_secs()
                recheck_counter = 0
                while remainingSeconds > 0:
                    try:
                        print("\rWainting for the song to end in " + remainingSeconds.__str__(), end = '    ', flush=True)
                        remainingSeconds -= 1
                        time.sleep(1)
                        recheck_counter += 1
                        # resync the remaining time every 10 seconds
                        if recheck_counter == 10:
                            recheck_counter = 0
                            remainingSeconds = self._curr_track_remaining_secs()
                    except KeyboardInterrupt:
                        print("\nCancelled by user!")
                        return 1
                songs -= 1
            print()
            self.pause()
        else:
            print("Nothing is playing!!")

    def _curr_track_remaining_secs(self):
        current_track = self.get_current_track_info()
        position = dateutil.parser.parse(current_track['position'])
        duration = dateutil.parser.parse(current_track['duration'])
        remainingSeconds = (duration - position).seconds
        return remainingSeconds

class SonosExtrasCliHelper(SonosExtras):
    def print_queue(self, starting_index = 1, number_of_tracks = 0):
        count = starting_index

        batches = max(100, number_of_tracks)
        queue = self.get_queue(starting_index, batches)
        
        if number_of_tracks == 0: 
            return_rest = True
            tracks_to_return = queue.total_matches - starting_index
        else:
            return_rest = False
            tracks_to_return = number_of_tracks
            
        print("Total " + queue.total_matches.__str__() + " items in queue:")
        returned_matches = queue.number_returned
        
        while (tracks_to_return > returned_matches and queue.number_returned > 0) :
            for item in queue:
                try:
                    item_dict = item.__dict__
                    item_dict["uri"] = item_dict["resources"][0].__str__()
                    if "creator" in item_dict.keys():
                        item_dict["artist"] = item_dict["creator"] 
                    else:
                        item_dict["artist"] = "N/A"
                    if 'album' in item_dict.keys(): 
                        item_dict["album"] = item_dict["album"] 
                    else:
                        item_dict["album"] = "N/A"
                    if "metadata" in item_dict.keys():
                        if "title" in item_dict['metadata'].keys():
                            item_dict["title"] = item_dict['metadata']["title"]
                    item_dict["mycount"] = count
                    # print(item_dict)
                    self.print_track(item_dict)
                    count = count + 1
                except:
                    print("Unexpected error:", sys.exc_info()[0])
            queue = self.get_queue(returned_matches + starting_index)
            returned_matches = returned_matches + queue.number_returned
        
    def print_current_status(self):
        print(self.get_current_transport_info())
        current_track = self.get_current_track_info()
        print(current_track['position'], ' / ', current_track['duration'])
        self.print_track(current_track)

    def print_track(self, track):
        line = ''
        if "playlist_position" in track.keys(): 
            line = track["playlist_position"] + " | "
        else: 
            line = track["mycount"].__str__() + " | "
        if track["artist"]  != '': line = line + track["artist"] + " | "
        if track["album"]   != '': line = line + track["album"] + " | "
        if track["title"]   != '': line = line + track["title"] + " | "
        if track["uri"]   != '': line = line + track["uri"]
        print(line)

    def playlists(self):
        allLists = self.get_sonos_playlists()
        for ourList in allLists:
            print(ourList.item_id + " | " + ourList.title)
        print("Total: " + allLists.number_returned.__str__())
    
    def playlist(self, title):
        try:
            ourList = self.get_sonos_playlist_by_attr('title', title)
        except ValueError:
            try:
                ourList = self.get_sonos_playlist_by_attr('item_id', title)
            except ValueError:
                print("No playlist matched " + title)
                return

        print("playlist " + title + " exists")
