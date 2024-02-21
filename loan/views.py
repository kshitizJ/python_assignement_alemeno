from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from customer.models import Customer
from customer.views import calculate_monthly_installment, check_eligibility
from .models import Loan
from .serializers import LoanSerializer

@api_view(['POST'])
def create_loan(request):
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

    # Check eligibility
    response = check_eligibility(request)
    approval = response.data.get('approval', False)
    corrected_interest_rate = response.data.get('corrected_interest_rate')

    # Set loan_approved based on eligibility
    loan_approved = approval and corrected_interest_rate is not None
    
    # Create the loan object
    loan = Loan.objects.create(
        customer=customer,
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        tenure=tenure,
        loan_approved=loan_approved
    )

    monthly_instalment = calculate_monthly_installment(loan_amount, interest_rate, tenure)

    # Prepare response data
    response_data = {
        "loan_id": loan.id,
        "customer_id": customer_id,
        "loan_approved": loan_approved,
        "message": "Loan created successfully",
        "monthly_installment": monthly_instalment
    }

@api_view(['GET'])
def view_loan_details(request, loan_id):
    try:
        loan = Loan.objects.get(pk=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan does not exist"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LoanSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)