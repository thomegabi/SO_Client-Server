import java.io.*;
import java.net.*;
import java.util.Scanner;
import java.util.Arrays;

public class Client {
    private static Socket socket;
    private static BufferedReader reader;
    private static PrintWriter writer;
    private static final String[] MESSAGES = {"list_dir", "sys_info", "mouse_control", "rotate_screen", "chat", "delete_user"};

    public static void main(String[] args) {
        try {
            socket = new Socket("localhost", 9999);
            reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            writer = new PrintWriter(socket.getOutputStream(), true);

            Scanner scanner = new Scanner(System.in);

            System.out.println("Conexão com o servidor estabelecida com sucesso!");

            // Autenticação
            boolean authenticated = false;
            while (!authenticated) {
                System.out.println("Digite 'login' para fazer login ou 'register' para se registrar:");
                String action = scanner.nextLine().trim().toLowerCase();
                if (action.equals("login") || action.equals("register")) {
                    System.out.println("Digite o nome de usuário:");
                    String username = scanner.nextLine().trim();
                    System.out.println("Digite a senha:");
                    String password = scanner.nextLine().trim();
                    String credentials = action + "|" + username + "|" + password;
                    writer.println(credentials);

                    String response = reader.readLine();
                    if (response == null) {
                        System.out.println("Erro na comunicação com o servidor. Tente novamente.");
                        continue;
                    }
                    if (response.equals("AUTH_SUCCESS")) {
                        authenticated = true;
                        System.out.println("Autenticação bem-sucedida.");
                    } else if (response.equals("REGISTER_SUCCESS")) {
                        authenticated = true;
                        System.out.println("Registro bem-sucedido.");
                    } else if (response.equals("USER_EXISTS")) {
                        System.out.println("Usuário já existe. Tente novamente.");
                    } else if (response.equals("AUTH_FAILED")) {
                        System.out.println("Autenticação falhou. Tente novamente.");
                    } else {
                        System.out.println("Ação inválida. Tente novamente.");
                    }
                } else {
                    System.out.println("Comando inválido. Digite 'login' ou 'register'.");
                }
            }

            Thread sendMessage = new Thread(() -> {
                try {
                    while (!Thread.currentThread().isInterrupted()) {
                        try {
                                Thread.sleep(1000); // Pausa a execução da thread por 2000 milissegundos (ou 2 segundos)
                        } catch (InterruptedException e) {
                                e.printStackTrace(); // Lida com a exceção se a thread for interrompida enquanto está dormindo
                            }
                        System.out.println("\nComandos possíveis: " + String.join(", ", MESSAGES));
                        System.out.print("Digite o comando: ");

                        String action = scanner.nextLine().trim();
                        if (isValidMessage(action)) {
                            String command = "";
                            if (!action.equals("sys_info")) {
                                if (action.equals("mouse_control")) {
                                    System.out.println("Parâmetros possíveis: limit, invert, punch, lock");
                                    System.out.println("Digite o comando do mouse:");
                                    command = scanner.nextLine().trim();
                                    if (command.equals("limit")) {
                                        System.out.println("Digite o tamanho da área ao redor:");
                                        int aroundSize = Integer.parseInt(scanner.nextLine().trim());
                                        while (aroundSize <= 0) {
                                            System.out.println("O tamanho da área ao redor deve ser maior que zero. Digite novamente:");
                                            aroundSize = Integer.parseInt(scanner.nextLine().trim());
                                        }

                                        System.out.println("Digite a duração em segundos:");
                                        int duration = Integer.parseInt(scanner.nextLine().trim());
                                        while (duration <= 0) {
                                            System.out.println("A duração deve ser maior que zero. Digite novamente:");
                                            duration = Integer.parseInt(scanner.nextLine().trim());
                                        }
                                        command = command + "|{" + "\"around_size\":" + aroundSize + ",\"duration\":" + duration + "}";
                                    } else if (command.equals("lock")) {
                                        command = "lock";
                                    } else if(command.equals("invert")){
                                        command = "invert";
                                    } else if(command.equals("punch")){
                                        command = "punch";
                                    }
                                } else if (action.equals("list_dir")) {
                                    System.out.println("Digite o caminho do diretório (ou deixe em branco para o diretório padrão):");
                                    command = scanner.nextLine().trim();
                                } else if (action.equals("rotate_screen")) {
                                    command = "";
                                } else if(action.equals("chat")){
                                    command = "chat";
                                    System.out.println("Digite a mensagem de chat (ou 'exits' para sair):");
                                    while (true) {
                                        //System.out.print("User: ");
                                        String chatMessage = scanner.nextLine().trim();
                                        writer.println(command + "|" + chatMessage);
                                        if (chatMessage.equalsIgnoreCase("exits")) {
                                            break;
                                        }
                                    }
                                } else if(action.equals("delete_user")){
                                    System.out.println("Digite o nome do usuário a ser deletado");
                                    command = scanner.nextLine().trim();
                                }
                                else {
                                    System.out.println("Digite o parâmetro do comando:");
                                    command = scanner.nextLine().trim();
                                }
                            }
                            String message = action + (command.isEmpty() ? "" : "|" + command);
                            writer.println(message);
                        } else {
                            System.out.println("Mensagem inválida. Tente novamente.");
                        }
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                } finally {
                    scanner.close();
                    writer.close();
                }
            });

            Thread receiveMessage = new Thread(() -> {
                try {
                    receive_message();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });

            receiveMessage.start();
            sendMessage.start();
            
            receiveMessage.join();
            sendMessage.join();
            

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        } finally {
            try {
                if (socket != null && !socket.isClosed()) {
                    socket.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private static void receive_message() throws IOException {
        while (true) {
            String message = reader.readLine();
            if (message == null) {
                System.out.println("Desconectado do servidor.");
                break;
            }
            System.out.println("\nServidor." + message);
        }
    }

    private static boolean isValidMessage(String message) {
        return Arrays.asList(MESSAGES).contains(message);
    }
}