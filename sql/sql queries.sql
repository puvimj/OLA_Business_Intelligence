--1. Retrieve all successful bookings:
SELECT 
	"Date"::date AS "DATE",
	"Time",
	"Booking_ID" AS "Booking ID",
	"Booking_Status" AS "Booking Status",
	"Customer_ID" AS "Customer ID",
	"Vehicle_Type" AS "Vehicle Type",
	"Pickup_Location" AS "Pickup Location",
	"Drop_Location" AS "Drop Location",
	"V_TAT" AS "Vehicle Turn Around Time",
	"C_TAT" AS "Customer Turn Around Time",
	"Canceled_Rides_by_Customer" AS "Canceled Rides by Customer",
	"Canceled_Rides_by_Driver" AS "Canceled Rides by Driver",
	"Incomplete_Rides" AS "Incomplete Rides",
	"Incomplete_Rides_Reason" AS "Incomplete Ride Reason",
	"Booking_Value" AS "Booking Value",
	"Payment_Method" AS "Payment Method",
	"Ride_Distance" AS "Ride Distance",
	"Driver_Ratings" AS "Driver Rating",
	"Customer_Rating" AS "Customer Rating",
	"Ride_Hour" AS "Ride Hour",
	"Ride_Day" AS "Ride Day",
	"Ride_Month" AS "Ride Month",
	CASE WHEN "Is_Weekend" THEN 'Yes' ELSE 'No' END AS "Is Weekend"
FROM "OLA_Bookings"
WHERE "Booking_Status" = 'Success' 
ORDER BY "Date" DESC;

--2. Find the average ride distance for each vehicle type:
SELECT
	"Vehicle_Type" AS "Vehicle Type",
	ROUND(AVG("Ride_Distance"),2) AS "Average Distance"
FROM "OLA_Bookings"
GROUP BY "Vehicle_Type"
ORDER BY "Average Distance" DESC;

--3. Get the total number of cancelled rides by customers:
SELECT COUNT(*) AS "Canceled Rides By Customers"
FROM "OLA_Bookings"
WHERE "Canceled_Rides_by_Customer" <> 'No' ;

--4. List the top 5 customers who booked the highest number of rides
SELECT
	"Customer_ID" AS "Customer ID",
	COUNT(*) AS "Number of Rides"
FROM "OLA_Bookings"
GROUP BY "Customer_ID"
ORDER BY "Number of Rides" DESC
LIMIT 5;

--5. Get the number of rides cancelled by drivers due to personal and car-related issues:
SELECT COUNT(*) AS "Canceled Rides By Driver"
FROM "OLA_Bookings"
WHERE "Canceled_Rides_by_Driver" = 'Personal & Car related issue' ;

--6. Find the maximum and minimum driver ratings for Prime Sedan bookings:
SELECT
	MAX("Driver_Ratings") AS "Max Rating",
	MIN("Driver_Ratings") AS "Min Rating"
FROM "OLA_Bookings"
WHERE "Vehicle_Type" = 'Prime Sedan';

--7. Retrieve all rides where payment was made using UPI:
SELECT 
	"Date",
	"Time",
	"Booking_ID" AS "Booking ID",
	"Booking_Status" AS "Booking Status",
	"Customer_ID" AS "Customer ID",
	"Vehicle_Type" AS "Vehicle Type",
	"Pickup_Location" AS "Pickup Location",
	"Drop_Location" AS "Drop Location",
	"V_TAT" AS "Vehicle Turn Around Time",
	"C_TAT" AS "Customer Turn Around Time",
	"Canceled_Rides_by_Customer" AS "Canceled Rides by Customer",
	"Canceled_Rides_by_Driver" AS "Canceled Rides by Driver",
	"Incomplete_Rides" AS "Incomplete Rides",
	"Incomplete_Rides_Reason" AS "Incomplete Ride Reason",
	"Booking_Value" AS "Booking Value",
	"Payment_Method" AS "Payment Method",
	"Ride_Distance" AS "Ride Distance",
	"Driver_Ratings" AS "Driver Rating",
	"Customer_Rating" AS "Customer Rating",
	"Ride_Hour" AS "Ride Hour",
	"Ride_Day" AS "Ride Day",
	"Ride_Month" AS "Ride Month",
	CASE WHEN "Is_Weekend" THEN 'Yes' ELSE 'No' END AS "Is Weekend"
FROM "OLA_Bookings"
WHERE "Payment_Method" = 'UPI'
ORDER BY "Date" DESC;

--8. Find the average customer rating per vehicle type:
SELECT
	"Vehicle_Type" AS "Vehicle Type",
	ROUND(
		AVG("Customer_Rating")::numeric, 2
	) AS "Average Customer Rating"
FROM "OLA_Bookings"
GROUP BY "Vehicle Type";
					
--9. Calculate the total booking value of rides completed successfully:
SELECT
	ROUND(SUM("Booking_Value"),2) AS "Revenue"
FROM "OLA_Bookings"
WHERE "Booking_Status" = 'Success';

--10. List all incomplete rides along with the reason
SELECT
	"Date",
	"Time",
	"Booking_ID" AS "Booking ID",
	"Booking_Status" AS "Booking Status",
	"Customer_ID" AS "Customer ID",
	"Vehicle_Type" AS "Vehicle Type",
	"Pickup_Location" AS "Pickup Location",
	"Drop_Location" AS "Drop Location",
	"V_TAT" AS "Vehicle Turn Around Time",
	"C_TAT" AS "Customer Turn Around Time",
	"Incomplete_Rides_Reason" AS "Incomplete Ride Reason",
	"Booking_Value" AS "Booking Value",
	"Payment_Method" AS "Payment Method",
	"Ride_Distance" AS "Ride Distance",
	"Driver_Ratings" AS "Driver Rating",
	"Customer_Rating" AS "Customer Rating",
	"Ride_Hour" AS "Ride Hour",
	"Ride_Day" AS "Ride Day",
	"Ride_Month" AS "Ride Month",
	CASE WHEN "Is_Weekend" THEN 'Yes' ELSE 'No' END AS "Is Weekend"
FROM "OLA_Bookings"
WHERE "Incomplete_Rides" = 'Yes'
ORDER BY "Date" DESC;