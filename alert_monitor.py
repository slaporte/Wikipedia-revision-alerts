# alertbot code from Twisted Matrix's irc_test.py

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.mail.smtp import sendmail
from email.mime.text import MIMEText
import alert_db as db
import time, sys, re, datetime

CHANNEL = 'en.wikipedia'
LOG = 'log'

def alert_terms(database='alerts'):
    ret = {}
    db.init(database)
    terms = db.Alert.select()
    for term in terms:
        ret.update(term.term_dict())
    return ret

def split_chat(chat):
    color_re = re.compile("\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
    no_color = color_re.sub('', chat)

    name_re = re.compile('\[\[(.*?)\]\]')
    url_re = re.compile(' http(.*?) ')
    summary_re = re.compile('\([\-\+][0-9]+\) (.*)')
    user_re = re.compile('\* (.*?) \*')
    rev_re = re.compile('oldid=([0-9]+)')

    try:
        ret =   {'summary': summary_re.search(no_color).group(1),
                'url': url_re.search(no_color).group(1),
                'name': name_re.search(no_color).group(1),
                'user': user_re.search(no_color).group(1),
                'revid': rev_re.search(no_color).group(1),
                }
    except:
        ret = {'error': 'attribute not found'}

    return ret

class Revision:
    def __init__(self, message):
        color_re = re.compile("\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
        no_color = color_re.sub('', message)

        name_re = re.compile('\[\[(.*?)\]\]')
        url_re = re.compile(' http(.*?) ')
        summary_re = re.compile('\([\-\+][0-9]+\) (.*)')
        user_re = re.compile('\* (.*?) \*')
        rev_re = re.compile('oldid=([0-9]+)')

        try:
            ret =   {'summary': summary_re.search(no_color).group(1),
                    'url': url_re.search(no_color).group(1),
                    'name': name_re.search(no_color).group(1),
                    'user': user_re.search(no_color).group(1),
                    'revid': rev_re.search(no_color).group(1),
                    }
        except:
            ret = {'error': 'attribute not found'}

        self.attr = ret

    def term(self, term):
        self.term = term

    def mail(self, recipient, term='unknown'):
        host = 'localhost'
        from_addr = 'wikipedia.monitor@example.com'
        to_addrs = [recipient]
        msg = MIMEText('Hello!\n\nThe page "' + self.attr['name'] + '" has been edited (see http://en.wikipedia.org/w/index.php?title=' + self.attr['name'].replace(' ', '_') + '&oldid=' + self.attr['revid'] + ').\n\nYou received this alert because it contained the term "' + self.term + '". Adjust your alert preferences here: http://localhost:8080/list/' + recipient + '\n\nCheers!')
        msg['Subject'] = 'Edit to ' + self.attr['name']
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_addrs)

        dfr = sendmail(host, from_addr, to_addrs, msg.as_string())
        def success(r):
            print r
        def error(e):
            print e
        dfr.addCallback(success)
        dfr.addErrback(error)


class MessageLogger:
    def __init__(self, file):
        self.file = file

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class AlertBot(irc.IRCClient):
    
    nickname = "AlertBot"
    rate = [datetime.datetime.now()]
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        self.logger.log("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        alert_list = alert_terms()
        for word in alert_list: 
            if word in msg:
                new_revision = Revision(msg)
                email = alert_list[word][0]
                if 'error' in new_revision.attr:
                    pass
                else:
                    self.logger.log("Match: %s; Title: %s; User: %s, Summary: %s" % (word, new_revision.attr['name'], new_revision.attr['user'], new_revision.attr['summary']))
                    new_revision.term(word)
                    new_revision.mail(email)
        #self.rate.append(datetime.datetime.now())
        #self.rate = [recent for recent in self.rate if recent > datetime.datetime.now() + datetime.timedelta(minutes=-1)]

class AlertBotFactory(protocol.ClientFactory):
    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p = AlertBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    
    f = AlertBotFactory(CHANNEL, LOG)

    reactor.connectTCP("irc.wikimedia.org", 6667, f)

    reactor.run()
