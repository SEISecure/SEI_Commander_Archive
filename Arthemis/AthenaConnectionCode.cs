using System;
using System.Net;
using System.Net.Sockets;
using AthenaMessages;
using ArtemisMessage;
using Google.Protobuf;
using System.Text;
using System.Threading;
namespace ConsoleApp2
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");
            /*           Principal_Athena_Message Message1 = new Principal_Athena_Message 
                       {
                           SenderId = 21351,
                           TimestampUtcTime = DateTime.Now.ToString()
                       };
                       Message1.MessageType = "Command";
                       //AthenaOrderMessage.Athena_Orders ord = new AthenaOrderMessage.Athena_Orders
                       //{
                       //    WeaponControlOrder = 3,
                       //    Behavior = 3
                       //};
                       //Message1.AthenaOrders.Add(ord);

                       Artemis_Message artMess1 = new Artemis_Message { };
                       artMess1.AmmoCount = 28;
                       artMess1.CurrentOrderRunning = "this is the order";
                       General_Order newOrder = new General_Order();
                       newOrder.Trigger = "general";
                       newOrder.WeaponControlOrder = 1;
                       newOrder.Behavior = 1;
                       artMess1.Orders.Add(newOrder);

                       Message1.Artemis.Add(artMess1);
                       //Artemis_Message artMess2 = new Artemis_Message
                       //{
                       //    AmmoCount = 228,
                       //    CurrentOrderRunning = "this is not an order"
                       //};
                       //Message1.Artemis.Add(artMess2);

                       Console.WriteLine("Message 1:    " + Message1.ToString() + "\n");

                      // string mess1JsonStr = Message1.ToByteArray();
                       //Principal_Athena_Message Message2 = Principal_Athena_Message.Parser.ParseJson(mess1JsonStr);
                       //Console.WriteLine("Message 2:    " + Message2.ToString());


                       IPAddress ipAddress = IPAddress.Parse("10.1.0.60");
                       IPEndPoint remoteEP = new IPEndPoint(ipAddress, 3636);

                       Socket sender = new Socket(ipAddress.AddressFamily, SocketType.Dgram, ProtocolType.Udp);
                       //string messageToSend = mess1JsonStr;
                       sender.Connect(remoteEP);
                       byte[] msg = Message1.ToByteArray(); ;// Encoding.ASCII.GetBytes(messageToSend);
                       Console.Beep(500, 500);

                       int bytesSent = sender.Send(msg);

                       Console.WriteLine("Message sent:    " + bytesSent);
            */
            //while (true)
            //{
                int arraySize = 100 * 1024;
                byte[] bytes = new byte[arraySize];
                //bytes[0] = 0;

                
                IPAddress ipAddress = IPAddress.Parse("10.1.2.196");
                //IPAddress ipAddress = IPAddress.Parse("10.1.0.60");
                IPEndPoint endPoint = new IPEndPoint(ipAddress, 3636);
                IPEndPoint sender = new IPEndPoint(IPAddress.Any, 0);
                EndPoint senderRemote = sender;

                Console.WriteLine("waiting");
                Socket receiver = new Socket(ipAddress.AddressFamily, SocketType.Dgram, ProtocolType.Udp);
                receiver.Bind(endPoint);
                int bytesRec = receiver.ReceiveFrom(bytes, 0, bytes.Length, SocketFlags.None, ref senderRemote);
                string receivedMessage = Encoding.ASCII.GetString(bytes, 0, bytesRec);
                Console.Write("received message : " + receivedMessage + "\n\n");
                //Principal_Athena_Message Message2 = new Principal_Athena_Message();
                //if (bytes[0] != 0)
                //{
                    Principal_Athena_Message Message2 = Principal_Athena_Message.Parser.ParseFrom(bytes, 0, bytesRec);
                
                Console.WriteLine("Message 2:    " + Message2.ToString());
                //}
                Thread.Sleep(1000);
            //}
        }
    }
}
