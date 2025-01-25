from app.shared.infrastructure.events.rabbitmq_configurer import RabbitMQConfigurer

rabbitmq_configurer: RabbitMQConfigurer | None = None


class RabbitMQConfigurerFactory:
    @classmethod
    def create(cls) -> RabbitMQConfigurer:
        global rabbitmq_configurer
        if rabbitmq_configurer is None:
            rabbitmq_configurer = RabbitMQConfigurer()
        return rabbitmq_configurer
