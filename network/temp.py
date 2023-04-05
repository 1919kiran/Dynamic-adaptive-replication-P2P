import pika
import multiprocessing as mp


# Function for the publisher process
def publisher():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body='Hello, RabbitMQ!')
    print(" [x] Sent 'Hello, RabbitMQ!'")
    connection.close()


# Function for the subscriber process
def subscriber(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(queue=queue_name,
                          auto_ack=True,
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    # Start the publisher process
    publisher_process = mp.Process(target=publisher)
    publisher_process.start()

    # Create a pool of subscriber processes
    num_subscribers = 4  # Number of subscriber processes
    subscriber_pool = mp.Pool(num_subscribers)
    queue_names = ['hello' + str(i) for i in range(num_subscribers)]  # Generate unique queue names for each subscriber
    subscriber_pool.map(subscriber, queue_names)

    # Wait for all processes to complete
    publisher_process.join()
    subscriber_pool.close()
    subscriber_pool.join()
