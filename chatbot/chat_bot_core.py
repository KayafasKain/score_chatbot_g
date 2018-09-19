from django.apps import apps
from urllib import request, parse
import json
from django.conf import settings
from .serializers import CreditRequestSerializerCRUD
from django.forms.models import model_to_dict
import re

Consumer = apps.get_model('chatbot', 'Consumer')
TelegramProfile = apps.get_model('chatbot', 'TelegramProfile')
CreditRequest = apps.get_model('chatbot', 'CreditRequest')


class ChatBotCore:
    '''
    Handling bot activities
    '''

    commands = [
        '/info',
        '/register',
        '/newloan'
    ]

    fields = {
        'seniority': 'Work seniority. Represented in years',
        'home': 'Home ownership. (rent, owner, partners, private, other, ignore)',
        'time': 'Time of loan, represented in months.',
        'age': 'Loaner age. Represented in years.',
        'marital': 'Marital status. (married. widow, single, separated, divorced)',
        'records': 'Represents other loans',
        'job': 'Represents type of job. (freelance, fixed, partime, others)',
        'expenses': 'Represents monthly expenses',
        'income': 'Represents monthly income',
        'assets': 'Represents assets',
        'amount': 'Loan amount',
        'price': 'Loan price',
        'finrat': 'Finantial rating',
        'savings': 'Loaner`s savings'
    }

    home_ownership = {
        'rent': 0,
        'owner': 1,
        'parents': 2,
        'private': 3,
        'other': 4,
        'ignore': 5
    }
    marital_status = {
        'married': 0,
        'widow': 1,
        'single': 2,
        'separated': 3,
        'divorced': 4
    }
    records_status = {
        'yes': 1,
        'no': 0
    }
    job_status = {
        'freelance': 0,
        'fixed': 1,
        'partime': 2,
        'others': 3
    }

    def __init__(self, request, TelegramBot):
        '''
        Taking request object from MessageLoop
        '''

        self.request = request
        self.TelegramBot = TelegramBot
        self.chat_id = request['chat']['id']
        self.parse_request(request.get('text'))

    def parse_request(self, request_text):
        '''
        Here goes request parsing and following handling, regarding redcived commands
        '''
        if '/register' in request_text:
            self.register_sequence(request_text)
        elif '/info' in request_text:
            self.info_sequence()
        elif '/newloan' in request_text:
            self.newloan_seqence(request_text)
        elif '/score last' in request_text:
            self.score_last()

    def register_sequence(self, request_text):
        '''
        These method parses, and executes commands related to registration
        '''
        if 'name' in request_text:
            self.reg_name(request_text)
        elif 'phone' in request_text:
            self.reg_phone(request_text)
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Tell me your full name, such as: "/register name: Ivanov Ivan"')

    def reg_phone(self, request_text):
        '''
        handling phone while registration
        '''
        phone = re.findall(r'\+380\d{3}\d{2}\d{2}\d{2}$', request_text)
        try:
            consumer_pk = TelegramProfile.objects.get(chat_id=self.chat_id).consumer.pk
            consumer = Consumer.objects.get(pk=consumer_pk)
            consumer.phone_number = phone[0]
            consumer.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please, tell me correct phone number')
        else:
            self.TelegramBot.sendMessage(self.chat_id,
                                         'Nice! Thank you for registration! You can check your credit score now!'
                                         )

    def reg_name(self, request_text):
        '''
        Handling fullname while registration
        '''
        consumer_fname = re.findall(r'[A-z]+', request_text)
        try:
            consumer = Consumer()
            consumer.first_name = consumer_fname[2]
            consumer.second_name = consumer_fname[3]
            consumer.save()
            tel_prof = TelegramProfile()
            tel_prof.chat_id = self.chat_id
            tel_prof.consumer = consumer
            tel_prof.save()

        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please, tell me correct full name')
        else:
            self.TelegramBot.sendMessage(self.chat_id,
                                         'Nice! Now, tell me your mobile phone, such as: /register phone:' +
                                         ' +380NNNNNNNNN'
                                         )

    def newloan_seqence(self, request_text):
        if  'create' in request_text:
            self.nl_new()
        else:
            consumer = TelegramProfile.objects.get(chat_id=self.chat_id).consumer
            self.cr_req = CreditRequest.objects.filter(consumer=consumer).order_by('-created')[0]
        if 'seniority' in request_text:
            self.nl_seniority(request_text)
        elif 'home' in request_text:
            self.nl_home(request_text)
        elif 'time' in request_text:
            self.nl_time(request_text)
        elif 'age' in request_text:
            self.nl_age(request_text)
        elif 'marital' in request_text:
            self.nl_marital(request_text)
        elif 'records' in request_text:
            self.nl_records(request_text)
        elif 'job' in request_text:
            self.nl_job(request_text)
        elif 'expenses' in request_text:
            self.nl_expenses(request_text)
        elif 'income' in request_text:
            self.nl_income(request_text)
        elif 'assets' in request_text:
            self.nl_assets(request_text)
        elif 'debt' in request_text:
            self.nl_debt(request_text)
        elif 'amount' in request_text:
            self.nl_amount(request_text)
        elif 'price' in request_text:
            self.nl_price(request_text)

    def score_last(self):
        # find last loan record
        consumer = TelegramProfile.objects.get(chat_id=self.chat_id).consumer
        cr_req = CreditRequest.objects.filter(consumer=consumer).order_by('-created')[0]

        #prepeare request to foreign api
        req = request.Request(settings.CLASSIFIER_URL + 'api/dataset/')
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(model_to_dict(cr_req))
        jsondataasbytes = jsondata.encode('utf-8')
        req.add_header('Content-Length', len(jsondataasbytes))

        # sending request
        response = request.urlopen(req, jsondataasbytes)
        encoding = response.info().get_content_charset('utf-8')

        status_ml = json.loads(response.read().decode(encoding))['status_ml']
        if status_ml == 1:
            self.TelegramBot.sendMessage(self.chat_id, 'Gratz! You can take these loan!')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'I am not certain about you, please contact humans instead.')
        cr_req.status_ml=status_ml
        cr_req.save()

    def nl_new(self):
        try:
            consumer = TelegramProfile.objects.get(chat_id=self.chat_id).consumer
            cr_req = CreditRequest()
            cr_req.consumer = consumer
            cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Something went wrong...')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Tell me about your seniority! "/newloan seniority: 21"')

    def nl_amount(self, request_text):
        '''
        Handling info about loan amount
        '''
        amount = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.amount = int(amount)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please enter correct data!')
        else:
            self.TelegramBot.sendMessage(self.chat_id,
                                         'Nice! Now tell me, how many you expect to return. "/newloan price: 1040"')

    def nl_debt(self, request_text):
        '''
        Handling info about current debts
        '''
        debt = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.debt = int(debt)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please enter correct data!')
        else:
            self.TelegramBot.sendMessage(self.chat_id,
                                         'Nice! Now tell me, how many you expect to get. "/newloan amount: 1000"')

    def nl_assets(self, request_text):
        '''
        Handling User`s assets data
        '''
        assets = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.assets = int(assets)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please enter correct data!')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Nice! Now tell me, summ of your debts. "/newloan debt: 0"')

    def nl_income(self, request_text):
        '''
        Handling income info
        '''
        income = re.findall(r'[0-9]+',request_text)[0]
        try:
            self.cr_req.income = int(income)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please, provide with valid income data!')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Nice! Now tell me about your assets "/newloan assets: 1000"')

    def nl_expenses(self, request_text):
        '''
        Handling client expenses
        '''
        expenses = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.expenses = int(expenses)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please, provide me with valid dataa')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Nice! Now tell me about your income.')

    def nl_job(self, request_text):
        '''
        Handeling job info
        '''
        job = re.findall(r'freelance|fixed|partime|others', request_text)[0]
        try:
            self.cr_req.job = self.job_status[job]
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please provide me with correct data!')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Nice! Now tell me about your expenses! "/newloan expenses: 1000"')

    def nl_records(self, request_text):
        '''
        Handeling info about previous credit records
        '''
        records = re.findall(r'yes|no', request_text)[0]
        try:
            self.cr_req.records = self.records_status[records]
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'So, have you any records? Yes or no?')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Nice! Now tell me about your job! "/newloan job: freelance"')

    def nl_seniority(self, request_text):
        '''
        Handling seniority
        '''
        seniority = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.seniority = int(seniority)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please, tell me correct info about your seniority')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Nice!Now, tell me about your home. /newloan home:' +
                                         self.fields['home']
                                         )

    def nl_home(self, request_text):
        '''
        Handling info about home ownership
        '''
        home = re.findall(r'rent|owner|parents|private|other|ignore', request_text)[0]
        try:
            self.cr_req.home = int(self.home_ownership[home])
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please, provide me with correct data!')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'How long will it take for you, to pay out the loan?(months)' +
                                        '"/newloan time: 12"'
                                         )

    def nl_time(self, request_text):
        '''
        Handling time for loan to paid off
        '''
        time = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.time = int(time)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please give me correct time!')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Nice! Now tell me, how old are you?')

    def nl_age(self, request_text):
        '''
        These method handels data about consumer age
        '''
        age = re.findall(r'[0-9]', request_text)[0]
        try:
            self.cr_req.age = int(age)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please, don`t hide your real age from me!')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Nice! Are you merried? "/newloan marital: married "')

    def nl_marital(self, request_text):
        '''
        These method handels marital status
        '''
        marita = re.findall(r'married|single|widow|separated|divorced', request_text)[0]
        try:
            self.cr_req.marital = self.marital_status[marita]
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please, provide me with valid marital data!')
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'Nice! Are you have any credit records? "/newloan records: yes"')

    def nl_price(self, request_text):
        '''
        Handling info about loan price
        '''
        price = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.price = int(price)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, 'Please enter correct data!')
        else:
            self.TelegramBot.sendMessage(self.chat_id,
                                         'Done! Now you can check credit chance! "/score last"')

    def info_sequence(self):
        pass


