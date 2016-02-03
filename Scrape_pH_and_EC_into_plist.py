
#===============================================================================
# This script scrapes the pH and EC values for herbs and vegetables from the
# homehydrosystems.com web site.  I am using the values from this web site because
# when I googled for something like 'pH basil', a page on this web site was at the
# top of a Google search.  Another site might have different values for pH and EC....
# For now I feel getting the pH and EC values this way is "good enough".
# honehydrosystems.com
#===============================================================================
#*******************************************************************************
#===============================================================================
# Takes in either the table entry for the pH value or EC value.  Converts the text
# range into values from which the value used by the Ladybug system will be the
# midpoint.  Checks are made to make sure the values are actually in the string
# being passed in.  A string is returned that represents either the pH or EC value.
# For example, the pH value in the table for basil is 5.5-6.5 .  The input string is
# '5.5-6.5' .  The string value returned is '6.0' .

#===============================================================================
def getValue(aStringRepresentingApHorECRange):
    twoFloats = aStringRepresentingApHorECRange.split('-')
    try:
        firstFloat = float(twoFloats[0])
        try:
            secondFloat = float(twoFloats[1])
        except:
            secondFloat = 0.0
    except:
        #=======================================================================
        # If the first isn't a float then there is no value to return.
        #=======================================================================
        return None
    #===========================================================================
    # Get the middle point as the value to use
    #===========================================================================
    returnValue = (secondFloat + firstFloat)/2.0
    #===========================================================================
    # Keep the precision to .1
    #===========================================================================
    returnValueString = "{:.1f}".format(returnValue)
    return returnValueString

import urllib2
print urllib2.__file__
from bs4 import BeautifulSoup
#===============================================================================
# There are two web pages that I am scraping to get the pH and EC info.  One is for herbs: http://www.homehydrosystems.com/ph_tds_ppm/ph_herbs_page.html
# The other is for vegetables: http://www.homehydrosystems.com/ph_tds_ppm/ph_vegetables_page.html
#=============================================================================== 
urls = ['http://www.homehydrosystems.com/ph_tds_ppm/ph_herbs_page.html','http://www.homehydrosystems.com/ph_tds_ppm/ph_vegetables_page.html']
#===============================================================================
# This function converts the range of pH or EC values found on a homehydrosystems.com entry, takes the midpoint (if there are two points) and creates a float.
# For example, the basil entry has a pH = '5.5-6.5'.  The float value is 6.0.  This is the value to be used by the Ladybug system.
#===============================================================================
#===============================================================================
# This is the output plist file that can be read in by the iOS app to get the data into a database the iOS app accesses.
#===============================================================================
with open('pH_and_EC_values.plist', 'w') as plistfile:
    #===========================================================================
    # Write the plist file's header
    #===========================================================================
    plistfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    plistfile.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
    plistfile.write('<plist version="1.0">\n')
    plistfile.write('<dict>\n')
    for url in urls:
        #=======================================================================
        # Open web page that has pH and EC info for plants.
        # There are two web pages.
        #=======================================================================
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError,err:
            if err.code == 404:
                print "Page not found."
            elif err.code == 403:
                print "Access denied."
            else:
                print "Error....error code:",err.code
        except urllib2.URLError, err:
            print "Error before HTTP connection could happen.  The reason given:",err.reason
            #===================================================================
            # Parse the html into an object where the table holding the EC and pH values will be extracted.
            #===================================================================
        html = response.read()
        soup = BeautifulSoup(html,"html.parser")
        #=======================================================================
        # Got table code from a stackoverflow answer found here: http://stackoverflow.com/questions/23377533/python-beautifulsoup-parsing-table.
        #=======================================================================
        table = soup.find('table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        #===================================================================
        # Skip the first row of the 2nd file since the csv will use the header from the 1st file.
        #===================================================================
        if url == urls[1]:
            rows = rows[1:]
        for row in rows:
            #===================================================================
            # Each row contains plant name (0), pH (1), cF (2), EC (3), and PPM (4).  We need only the plant name, pH, and EC.
            # So don't include the cF and PPM columns in the csv file.
            #===================================================================
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if (url == urls[0]) and (row == rows[0]):
                cols[0] = 'plant'
            del cols[2]
            #===================================================================
            # Now the columns = plant name (0), pH(1),EC(2), and PPM(3).  Deleting PPM means not including the 3rd column at this point.
            #===================================================================
            del cols[3] 
            #===================================================================
            # Don't include rows that have an empty pH or EC value.
            #===================================================================
            if cols[1] and cols[2]:
                #===============================================================
                # Some of the plant names have a \n between words of name.  For example: Bell\npeppers
                #===============================================================
                cols[0] = cols[0].replace('\n',' ')
                if (cols[1] != 'pH'):   
                #===============================================================
                # The pH and EC values have a range, like 5.5-6.5.  Use the half-way point.
                #===============================================================
                    cols[1] = getValue(cols[1])           
                    cols[2] = getValue(cols[2])
                    print "%r pHValue: %r   ECValue: %r" %(cols[0],cols[1],cols[2])
                    plistfile.write('\t<key>' + cols[0] + '</key>\n')
                    plistfile.write('\t<dict>\n')
                    plistfile.write('\t\t<key>pH</key>\n')
                    plistfile.write('\t\t<string>' + cols[1] + '</string>\n')
                    plistfile.write('\t\t<key>EC</key>\n')
                    plistfile.write('\t\t<string>' + cols[2] + '</string>\n')
                    plistfile.write('\t</dict>\n')
    plistfile.write('</dict>\n')
    plistfile.write('</plist>\n')      
    print 'Success!'