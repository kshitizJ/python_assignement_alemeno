import datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from loan.serializers import LoanSerializer
from .models import Customer
from .serializers import CustomerSerializer
from customer import models
from math import pow

@api_view(['POST'])
def register_customer(request):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        approved_limit = round(36 * serializer.validated_data['monthly_income'] / 100000) * 100000
        serializer.save(approved_limit=approved_limit)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_eligibility(request):
    customer_id = request.data.get('customer_id', None)
    loan_amount = request.data.get('loan_amount', None)
    interest_rate = request.data.get('interest_rate', None)
    tenure = request.data.get('tenure', None)

    if not all([customer_id, loan_amount, interest_rate, tenure]):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # Component i: Past Loans paid on time
    total_emis_paid_on_time = customer.loan_set.aggregate(total_emis_paid_on_time=models.Sum('emis_paid_on_time'))['total_emis_paid_on_time'] or 0

    # Component ii: No of loans taken in past
    total_loans_taken = customer.loan_set.count()

    # Component iii: Loan activity in current year
    current_year = datetime.now().year
    loans_in_current_year = customer.loan_set.filter(start_date__year=current_year).count()

    # Component iv: Loan approved volume
    total_loan_approved = customer.loan_set.aggregate(total_loan_approved=models.Sum('loan_amount'))['total_loan_approved'] or 0

    # Component v: If sum of current loans of customer > approved limit of customer, credit score = 0
    sum_current_loans = customer.loan_set.aggregate(sum_current_loans=models.Sum('loan_amount'))['sum_current_loans'] or 0

    approved_limit = customer.approved_limit

    if sum_current_loans > approved_limit:
        credit_score = 0
    else:
        credit_score = (total_emis_paid_on_time / (total_loans_taken + 1)) * 20 \
                       + (loans_in_current_year * 10) \
                       + ((total_loan_approved / approved_limit) * 30) \
                       - ((sum_current_loans / approved_limit) * 20)

    if credit_score > 50:
        approval = True
    elif 30 < credit_score <= 50:
        approval = interest_rate > 12
    elif 10 < credit_score <= 30:
        approval = interest_rate > 16
    else:
        approval = False

    # Check if sum of all current EMIs > 50% of monthly salary
    if approval:
        sum_current_emis = customer.loan_set.aggregate(sum_current_emis=models.Sum('monthly_repayment'))['sum_current_emis'] or 0
        if sum_current_emis > customer.monthly_income * 0.5:
            approval = False

    # Correct the interest rate if it doesn't match as per credit limit
    if approval:
        if credit_score > 50:
            corrected_interest_rate = interest_rate
        elif 30 < credit_score <= 50:
            corrected_interest_rate = max(interest_rate, 12)
        elif 10 < credit_score <= 30:
            corrected_interest_rate = max(interest_rate, 16)
        else:
            corrected_interest_rate = 0  # This can be any value as the loan won't be approved

    monthly_instalment = calculate_monthly_installment(loan_amount, interest_rate, tenure)

    response_data = {
        "customer_id": customer_id,
        "approval": approval,
        "interest_rate": interest_rate,
        "corrected_interest_rate": corrected_interest_rate if approval else None,
        "tenure": tenure,
        "monthly_instalment": monthly_instalment 
    }

    return Response(response_data, status=status.HTTP_200_OK)


def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    # Convert interest rate from percentage to decimal
    monthly_interest_rate = interest_rate / (12 * 100)
    
    # Calculate EMI using formula
    emi = (loan_amount * monthly_interest_rate * pow(1 + monthly_interest_rate, tenure)) / (pow(1 + monthly_interest_rate, tenure) - 1)
    
    return emi

@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    # Retrieve all loans for a specific customer
    customer = Customer.objects.get(pk=customer_id)
    loans = customer.loan_set.all()
    serializer = LoanSerializer(loans, many=True)
    return Response(serializer.data)