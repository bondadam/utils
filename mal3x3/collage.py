#!/usr/bin/env python

import urllib2
import urllib
import xml.etree.ElementTree as ET
import os
import sys
import argparse
from PIL import Image
from PIL import ImageFont, ImageDraw

def getHighestRated(listAnime, size):
    """Return list of highest rated anime/manga, with [size*size] xml elements.
    Doesn't take into account unrated media.

    Keyword arguments:
    listAnime -- list of anime or manga MAL xml elements
    size -- number of elements to return
    """
    if len(listAnime) == 0:
        raise Exception("User's list is empty.")
    listAnimeTemp = listAnime[:]
    listHighestRated = []
    for i in xrange(min(size, len(listAnime))):
            bestMark = -1
            for element in listAnimeTemp:
                if int(element.find('my_score').text) > bestMark:
                    bestMark = int(element.find('my_score').text)
                    seriesBestMark = element
            listHighestRated.append(seriesBestMark)
            listAnimeTemp.remove(seriesBestMark)
    return listHighestRated

def getPictures(listAnime):
    """Return list of strings containing URLS of pictures for given anime/manga.

    Keyword arguments:
    listAnime -- list of anime or manga MAL xml elements
    """
    listPictures = []
    for anime in listAnime:
        listPictures.append(anime.find('series_image').text)
    return listPictures

def cropPictures(listPictures, width = 225, height = 300):
    """Return given list of Pillow Image elements cropped to given size. Default is 225x300 because that seems to be the standard MAL size.

    Keyword arguments:
    listPictures -- list of Pillow Image elements
    width -- 
    """
    pictures = []
    for i in listPictures:
        if (i.size[0] > width) or (i.size[1] > height):
            marginHorizontal = (i.size[0] - width)/2
            marginVertical = (i.size[1] - height)/2
            pictures.append(i.crop([marginHorizontal, marginVertical, marginHorizontal + width, marginVertical + height]))
        else:
            pictures.append(i)
    return listPictures

def getTitles(listAnime):
    delchars = ''.join(c for c in map(chr, range(256)) if not c.isalnum())
    titles = []
    for anime in listAnime:
        titles.append([anime.find('series_title').text, anime.find('series_title').text.encode('utf-8').translate(None, delchars)])
    return titles

def drawCollage(pictures, endSizeX, endPicture, singleWidth = 225, singleHeight = 300):
    xpos = 0
    ypos = 0
    for i in pictures:
            if (xpos > (endSizeX - singleWidth)):
                       xpos = 0
                       ypos += singleHeight
            endPicture.paste(i,[xpos, ypos])
            xpos += singleWidth

def drawTitles(titles, endSizeX, endPicture):
    xpos = 0
    ypos = 0
    for i in titles:
            if (xpos > (endSizeX - 225)):
                       xpos = 0
                       ypos += 300
            draw.text(i,[xpos, ypos])
            xpos += 225

def isValidUsername(username):
    ## MAL only allows letters, numbers, underscores and dashes
    ## username must be 2 < x < 16 characters
    if len(username) < 2 or len(username) > 16:
        return False
    for letter in username:
        if not letter.isalnum() and letter != "_" and letter != "-":
            return False
    return True

def main():
    """
    Args:
        string username
        string "manga" or "anime"
        string "true " or "false" to toggle titles display in sidebar
        int     3 or 4 or 5, size of chart (3 - > 3x3 = 9 images)
        string path where image output should be placed. default is current dir/public/images/collage
    """
    parser = argparse.ArgumentParser(description='Make collage of MAL anime or manga list.')
    parser.add_argument('username', type = str, help='MAL username')
    parser.add_argument('media type', type = str, default="anime", choices=['anime', 'manga'], help='manga or anime')
    parser.add_argument('titleToggled', type = str, default="false", choices=['true', 'false'], help='true to display titles in the sidebar, false otherwise')
    parser.add_argument('size', type = int, default=3, choices=[3,4,5], help='Collage size. 3, 4 or 5. 3 - > 3x3 -> 9 images, etc.')
    parser.add_argument('--path', type = str, default=os.getcwd() + "/public/images/collage/", help='path for result image')
    parser.add_argument('--save', help="Save downloaded pictures.", action="store_true")
    

    args = parser.parse_args()
    argsDictionary = vars(args)


    username = argsDictionary['username']
    mediaType = argsDictionary['media type']
    titleToggled = argsDictionary['titleToggled']
    size = argsDictionary['size']
    basePath = argsDictionary['path']
    saveToggled = argsDictionary['save']

    saveDirectory = os.path.join(os.getcwd(), mediaType + "Images")


    try:

        if not isValidUsername(username):
            raise Exception("""You must enter a valid username. MAL usernames are between 2 and 16 characters 
                long and composed of letters, numbers, dashes and underscores.""")

        endFilename = os.path.join(basePath, username + ".jpg")
        endSizeX = 225 * size
        endSizeY = 300 * size

        font = ImageFont.truetype("regroboto.ttf", 15)
        baseUrl = "https://myanimelist.net/malappinfo.php?u=" + username + "&status=all&type=" + mediaType
        page = urllib2.urlopen(baseUrl)
        pageParsed = ET.parse(page).getroot()
        highestRated = getHighestRated(pageParsed.findall(mediaType), size*size)

        listLength = len(highestRated)

        pictures = getPictures(highestRated)
        picturesUsed = []
        titles = getTitles(highestRated)

        if saveToggled and not os.path.isdir(saveDirectory):
            os.makedirs(saveDirectory)

        for i in xrange(len(pictures)):
            file_name = os.path.join(saveDirectory, titles[i][1] + ".jpg")
            if not os.path.isfile(file_name):
                urllib.urlretrieve(pictures[i], file_name)
            picturesUsed.append(Image.open(file_name))

        endPicture = Image.new("RGB",[endSizeX, endSizeY])
        draw = ImageDraw.Draw(endPicture)
        xpos = 0
        ypos = 0
        picturesUsed = cropPictures(picturesUsed)

        drawCollage(picturesUsed, endSizeX, endPicture)

        if titleToggled == "true":
            endPicture2 = Image.new("RGB",[endSizeX+200, endSizeY])
            endPicture2.paste(endPicture,[0,0])
            draw = ImageDraw.Draw(endPicture2)
            xPosNew = endSizeX + 5
            yPosNew = 20
            for i in xrange(listLength/size):
                for j in xrange(listLength):
                    if (len(titles[(i*size)+j][0])) < 20:
                        draw.text([xPosNew, yPosNew], titles[(i*size)+j][0], font = font, fill=(255,255,255,255))
                    else:
                        split_string = lambda x, n: [x[i:i+n] for i in xrange(0, len(x), n)]
                        toDraw = split_string(titles[(i*size)+j][0], 20)
                        for k in xrange(len(toDraw)):
                            #if toDraw[k][:1] != " " and k != (len(toDraw)-1):
                            #    toDraw[k] += "-"
                            draw.text([xPosNew, yPosNew], toDraw[k], font = font, fill=(255,255,255,255))
                            if k != (len(toDraw) - 1):
                                yPosNew += 20
                    yPosNew += 30
                yPosNew = ((i+1)*300)+20
            endPicture2.save(endFilename)
        else:
            endPicture.save(endFilename)
        print (os.path.relpath(endFilename))
    except Exception as e:
        sys.stderr.write(str(e))

if __name__ == '__main__':
    main()
