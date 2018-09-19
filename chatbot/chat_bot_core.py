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

    fields = {
        'seniority': 'Work seniority. Represented in years',
        'home': 'Home ownership. (rent, owner, partners, private, other, ignore)',
        'time': 'Time of loan, represented in months.',
        'age': 'Loaner age. Represented in years.',
        'marital': 'Marital status. (married. widow, single, separated, divorced)',
        'records': 'Represents other loans (yes, no)',
        'job': 'Represents type of job. (freelance, fixed, partime, others)',
        'expenses': 'Represents monthly expenses',
        'income': 'Represents monthly income',
        'assets': 'Represents assets',
        'amount': 'Loan amount',
        'price': 'Loan price',
    }
    messages = {
        'register': {
            'msg': {
                'registrations_success': 'Nice! Thank you for registration! You can check your credit score now!',
                'provide_phone': 'Nice! Now, tell me your mobile phone, such as: /register phone: +380NNNNNNNNN',
                'provide_fullname': 'Tell me your full name, such as: "/register name: Ivanov Ivan"'
            },
            'err': {
                'incorrect_phone': 'Please, tell me correct phone number',
                'incorrect_fullname': 'Please, tell me correct full name',
            }
        },
        'err_common': {
            'wrong_data': 'Please enter correct data!',
            'unknown_error': 'Something went wrong',
        },
        'loan': {
            'loan_approved': 'You can take these loan',
            'loan_disapproved': 'I can not classify you, please contact humans',
            'new': {
                'seniority': 'Tell me about your seniority! "/newloan seniority: 21"',
                'price': 'Nice! Now tell me, how many you expect to return. "/newloan price: 1040"',
                'amount': 'Nice! Now tell me, how many you expect to get. "/newloan amount: 1000"',
                'debt': 'Nice! Now tell me, summ of your debts. "/newloan debt: 0"',
                'assets': 'Nice! Now tell me about your assets "/newloan assets: 1000"',
                'income': 'Nice! Now tell me about your income. /newloan income: 1000"',
                'expenses': 'Nice! Now tell me about your expenses! "/newloan expenses: 1000"',
                'job': 'Nice! Now tell me about your job! "/newloan job: freelance"',
                'home': 'Nice!Now, tell me about your home. /newloan home:' + fields['home'],
                'time': 'How long will it take for you, to pay out the loan?(months) "/newloan time: 12"',
                'age': 'Nice! How old are you? "/newloan age: 54"',
                'marital': 'Nice! Are you merried? "/newloan marital: married "',
                'records': 'Nice! Are you have any credit records? "/newloan records: yes"',
                'score': 'Done! Now you can check credit chance! "/score last"'
            }
        }
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
            self.info_sequence(request_text)
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
            self.TelegramBot.sendMessage(self.chat_id, self.messages['register']['msg']['provide_fullname'])

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
            self.TelegramBot.sendMessage(self.chat_id, self.messages['register']['err']['incorrect_phone'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['register']['err']['registrations_success'])

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
            self.TelegramBot.sendMessage(self.chat_id, self.messages['register']['err']['incorrect_fullname'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['register']['err']['provide_phone'])

    def info_sequence(self, request_text):
        if 'seniority' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['seniority'])
        elif 'home' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['home'])
        elif 'time' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['time'])
        elif 'age' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['age'])
        elif 'marital' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['marital'])
        elif 'records' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['records'])
        elif 'job' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['job'])
        elif 'expenses' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['expenses'])
        elif 'income' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['income'])
        elif 'assets' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['assets'])
        elif 'amount' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['amount'])
        elif 'price' in request_text:
            self.TelegramBot.sendMessage(self.chat_id, self.fields['price'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, 'I cannot understand you')

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
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['loan_approved'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['loan_disapproved'])
        cr_req.status_ml=status_ml
        cr_req.save()

    def nl_new(self):
        try:
            consumer = TelegramProfile.objects.get(chat_id=self.chat_id).consumer
            cr_req = CreditRequest()
            cr_req.consumer = consumer
            cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['unknown_error'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['seniority'])

    def nl_amount(self, request_text):
        '''
        Handling info about loan amount
        '''
        amount = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.amount = int(amount)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['price'])

    def nl_debt(self, request_text):
        '''
        Handling info about current debts
        '''
        debt = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.debt = int(debt)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['amount'])

    def nl_assets(self, request_text):
        '''
        Handling User`s assets data
        '''
        assets = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.assets = int(assets)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['debt'])

    def nl_income(self, request_text):
        '''
        Handling income info
        '''
        income = re.findall(r'[0-9]+',request_text)[0]
        try:
            self.cr_req.income = int(income)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['assets'])

    def nl_expenses(self, request_text):
        '''
        Handling client expenses
        '''
        expenses = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.expenses = int(expenses)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['income'])

    def nl_job(self, request_text):
        '''
        Handeling job info
        '''
        job = re.findall(r'freelance|fixed|partime|others', request_text)[0]
        try:
            self.cr_req.job = self.job_status[job]
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['expenses'])

    def nl_records(self, request_text):
        '''
        Handeling info about previous credit records
        '''
        records = re.findall(r'yes|no', request_text)[0]
        try:
            self.cr_req.records = self.records_status[records]
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['job'])

    def nl_seniority(self, request_text):
        '''
        Handling seniority
        '''
        seniority = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.seniority = int(seniority)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['home'])

    def nl_home(self, request_text):
        '''
        Handling info about home ownership
        '''
        home = re.findall(r'rent|owner|parents|private|other|ignore', request_text)[0]
        try:
            self.cr_req.home = int(self.home_ownership[home])
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['time'])

    def nl_time(self, request_text):
        '''
        Handling time for loan to paid off
        '''
        time = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.time = int(time)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['age'])

    def nl_age(self, request_text):
        '''
        These method handels data about consumer age
        '''
        age = re.findall(r'[0-9]', request_text)[0]
        try:
            self.cr_req.age = int(age)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['marital'])

    def nl_marital(self, request_text):
        '''
        These method handels marital status
        '''
        marita = re.findall(r'married|single|widow|separated|divorced', request_text)[0]
        try:
            self.cr_req.marital = self.marital_status[marita]
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['records'])

    def nl_price(self, request_text):
        '''
        Handling info about loan price
        '''
        price = re.findall(r'[0-9]+', request_text)[0]
        try:
            self.cr_req.price = int(price)
            self.cr_req.save()
        except:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['err_common']['wrong_data'])
        else:
            self.TelegramBot.sendMessage(self.chat_id, self.messages['loan']['new']['score'])


